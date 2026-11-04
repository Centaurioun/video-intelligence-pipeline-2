"""MEGA-16.4 — Closed Offline CLI & End-to-End Verification Entrypoint.

Supports two closed offline subcommands:
1. `run-offline` — executes the deterministic synthetic MEGA-08..14 -> MEGA-15 -> MEGA-16
   pipeline and prints or writes the canonical JSON `Mega1516OfflineReport`.
2. `verify-report` — reads and cryptographically verifies an existing `Mega1516OfflineReport`
   JSON file.

Strictly refuses:
- Forbidden execution, network, model-download, real-archive, FFmpeg, or export flags
- URL arguments (`http://`, `https://`, `s3://`, `gs://`, `file://`)
- Paths outside the fixed `outputs/vip_lab/synthetic-reports` root, symlinks,
  existing-file overwrites (no-clobber), traversal (`..`), or media paths
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys
from typing import Sequence

from vip_lab.common import VipLabError, canonical_json_bytes
from vip_lab.mega15.temporal_preflight import raise_mega15_error
from vip_lab.mega16.release_refusal import (
    run_mega15_16_offline_pipeline,
    verify_mega15_16_offline_report,
)

REFUSAL_CLI_FORBIDDEN_FLAG = "REFUSAL_CLI_FORBIDDEN_AUTHORITY_OR_EXECUTION_FLAG"
REFUSAL_CLI_URL_FORBIDDEN = "REFUSAL_CLI_REMOTE_URL_FORBIDDEN"
REFUSAL_CLI_OUTPUT_PATH_UNSAFE = "REFUSAL_CLI_OUTPUT_PATH_UNSAFE"
REFUSAL_CLI_INPUT_PATH_UNSAFE = "REFUSAL_CLI_INPUT_PATH_UNSAFE"

MAX_CLI_REPORT_BYTES = 16 * 1024 * 1024
_TRUSTED_SYNTHETIC_REPORT_ROOT = (
    Path(__file__).resolve().parents[3]
    / "outputs"
    / "vip_lab"
    / "synthetic-reports"
)

FORBIDDEN_CLI_FLAGS: tuple[str, ...] = (
    "--execute-ffmpeg",
    "--ffmpeg",
    "--ffprobe",
    "--real-archive",
    "--archive-root",
    "--download-models",
    "--load-weights",
    "--enable-network",
    "--cloud-provider",
    "--approve-human",
    "--mint-edit-plan",
    "--compile-handoff",
    "--authorize-production-export",
    "--promote-gate",
    "--owner-override",
    "--real",
    "--render",
    "--export",
    "--provider",
    "--download",
    "--upload",
)

URL_PREFIXES: tuple[str, ...] = (
    "http://",
    "https://",
    "s3://",
    "gs://",
    "file://",
    "ftp://",
    "ssh://",
)

FORBIDDEN_MEDIA_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".mp4",
        ".mov",
        ".mkv",
        ".avi",
        ".webm",
        ".wav",
        ".flac",
        ".mp3",
        ".aac",
        ".m4a",
        ".mxf",
        ".ts",
    }
)


def _scan_raw_argv_for_forbidden_tokens(argv: Sequence[str]) -> None:
    for token in argv:
        flag_name = token.split("=", 1)[0].strip()
        if flag_name in FORBIDDEN_CLI_FLAGS:
            raise_mega15_error(
                REFUSAL_CLI_FORBIDDEN_FLAG,
                f"Forbidden CLI flag {flag_name!r} is not permitted in offline synthetic preparation.",
            )
        lower_tok = token.strip().lower()
        for prefix in URL_PREFIXES:
            if lower_tok.startswith(prefix) or (
                "=" in lower_tok and lower_tok.split("=", 1)[1].startswith(prefix)
            ):
                raise_mega15_error(
                    REFUSAL_CLI_URL_FORBIDDEN,
                    f"Remote or URI locator {token!r} is forbidden in offline CLI.",
                )


def _validate_safe_output_path(raw_path: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path.strip() or "\x00" in raw_path:
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Invalid output path: {raw_path!r}",
        )
    p = Path(raw_path)
    if ".." in p.parts:
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Parent directory traversal ('..') is forbidden in output path: {raw_path!r}",
        )
    if p.suffix.lower() in FORBIDDEN_MEDIA_EXTENSIONS:
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Media file extension {p.suffix!r} is forbidden for offline JSON report output.",
        )
    if p.suffix.lower() != ".json":
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Offline report output must use a .json path, got {p.suffix!r}.",
        )
    p = _confine_synthetic_report_path(
        p, raw_path, REFUSAL_CLI_OUTPUT_PATH_UNSAFE
    )
    if p.is_symlink() or p.exists():
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Output path {raw_path!r} already exists or is a symlink; refusing to overwrite.",
        )
    parent = p.parent if str(p.parent) != "" else Path(".")
    if parent.is_symlink():
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Output parent directory {str(parent)!r} cannot be a symlink.",
        )
    return p


def _confine_synthetic_report_path(
    path: Path, raw_path: str, refusal_code: str
) -> Path:
    """Resolve relative report names under the fixed, code-trusted report root."""
    root = _TRUSTED_SYNTHETIC_REPORT_ROOT
    if not root.is_absolute():
        raise_mega15_error(
            refusal_code,
            "Configured synthetic-report root must be an absolute path.",
        )
    candidate = path if path.is_absolute() else root / path
    try:
        candidate.relative_to(root)
    except ValueError:
        raise_mega15_error(
            refusal_code,
            f"Report path {raw_path!r} is outside the trusted synthetic-report directory.",
        )
    return candidate


def _open_parent_directory_without_symlinks(
    path: Path, *, create_missing: bool = True
) -> int:
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    if path.is_absolute():
        current_fd = os.open(path.anchor, flags)
        components = path.parent.parts[1:]
    else:
        current_fd = os.open(".", flags)
        components = path.parent.parts

    try:
        for component in components:
            if component in ("", "."):
                continue
            try:
                next_fd = os.open(component, flags, dir_fd=current_fd)
            except FileNotFoundError:
                if not create_missing:
                    raise
                try:
                    os.mkdir(component, mode=0o700, dir_fd=current_fd)
                except FileExistsError:
                    pass
                next_fd = os.open(component, flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except OSError:
        os.close(current_fd)
        raise


def _atomic_write_new_file(path: Path, data: bytes) -> None:
    parent_fd: int | None = None
    output_fd: int | None = None
    created = False
    try:
        parent_fd = _open_parent_directory_without_symlinks(path)
        output_fd = os.open(
            path.name,
            os.O_CREAT
            | os.O_EXCL
            | os.O_WRONLY
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_fd,
        )
        created = True
        view = memoryview(data)
        offset = 0
        while offset < len(view):
            written = os.write(output_fd, view[offset:])
            if written <= 0:
                raise OSError("write returned no progress")
            offset += written
        os.close(output_fd)
        output_fd = None
        os.close(parent_fd)
        parent_fd = None
    except OSError as exc:
        if output_fd is not None:
            try:
                os.close(output_fd)
            except OSError:
                pass
        if created and parent_fd is not None:
            try:
                os.unlink(path.name, dir_fd=parent_fd)
            except OSError:
                pass
        if parent_fd is not None:
            try:
                os.close(parent_fd)
            except OSError:
                pass
        raise_mega15_error(
            REFUSAL_CLI_OUTPUT_PATH_UNSAFE,
            f"Refused unsafe or incomplete write to output path {str(path)!r}: {exc}",
        )


def _safe_read_report_file(raw_path: str) -> dict:
    if not isinstance(raw_path, str) or not raw_path.strip() or "\x00" in raw_path:
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Invalid input path: {raw_path!r}",
        )
    p = Path(raw_path)
    if ".." in p.parts:
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Parent directory traversal ('..') is forbidden in input path: {raw_path!r}",
        )
    if p.suffix.lower() != ".json":
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Input must be a JSON synthetic report, got {p.suffix!r}.",
        )
    p = _confine_synthetic_report_path(
        p, raw_path, REFUSAL_CLI_INPUT_PATH_UNSAFE
    )
    if p.is_symlink():
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Input report path {raw_path!r} must not be a symlink.",
        )
    parent_fd: int | None = None
    fd: int | None = None
    try:
        parent_fd = _open_parent_directory_without_symlinks(
            p, create_missing=False
        )
        fd = os.open(
            p.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("input report is not a regular file")
        chunks: list[bytes] = []
        remaining = MAX_CLI_REPORT_BYTES + 1
        while remaining:
            chunk = os.read(fd, remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw_bytes = b"".join(chunks)
    except OSError as exc:
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Failed to open input report path {raw_path!r}: {exc}",
        )
    finally:
        if fd is not None:
            os.close(fd)
        if parent_fd is not None:
            os.close(parent_fd)

    if len(raw_bytes) > MAX_CLI_REPORT_BYTES:
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Input report exceeds maximum allowed size ({MAX_CLI_REPORT_BYTES} bytes).",
        )
    try:
        parsed = json.loads(raw_bytes.decode("utf-8"))
    except Exception as exc:
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            f"Input report is not valid UTF-8 JSON: {exc}",
        )
    if not isinstance(parsed, dict):
        raise_mega15_error(
            REFUSAL_CLI_INPUT_PATH_UNSAFE,
            "Input report JSON root must be an object.",
        )
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vip-lab-mega16",
        description="MEGA-15/16 Offline Gate-3 Preparation, QC & Release-Refusal Verifier CLI",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    run_p = sub.add_parser(
        "run-offline",
        help="Run the deterministic synthetic MEGA-15/16 offline pipeline.",
    )
    run_p.add_argument(
        "--seed",
        type=int,
        default=20261102,
        help="Deterministic synthetic seed (default: 20261102).",
    )
    run_p.add_argument(
        "--output",
        type=str,
        default=None,
        help=(
            "Optional new JSON report path under outputs/vip_lab/synthetic-reports; "
            "relative paths are rooted there."
        ),
    )

    ver_p = sub.add_parser(
        "verify-report",
        help="Verify an existing Mega1516OfflineReport JSON file.",
    )
    ver_p.add_argument(
        "--input",
        type=str,
        required=True,
        help=(
            "Mega1516OfflineReport JSON path under outputs/vip_lab/synthetic-reports; "
            "relative paths are rooted there."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the MEGA-16 CLI and return exit code (0 on success, 2 on refusal)."""
    args_list = list(sys.argv[1:]) if argv is None else list(argv)
    try:
        _scan_raw_argv_for_forbidden_tokens(args_list)
        parser = build_parser()
        ns = parser.parse_args(args_list)

        if ns.subcommand == "run-offline":
            out_path: Path | None = None
            if ns.output is not None:
                out_path = _validate_safe_output_path(ns.output)
            report = run_mega15_16_offline_pipeline(seed=int(ns.seed))
            serialized = canonical_json_bytes(report.to_dict()).decode("utf-8")
            if out_path is not None:
                _atomic_write_new_file(out_path, (serialized + "\n").encode("utf-8"))
            else:
                sys.stdout.write(serialized + "\n")
            return 0

        if ns.subcommand == "verify-report":
            payload = _safe_read_report_file(ns.input)
            verified = verify_mega15_16_offline_report(payload)
            summary = {
                "verified": True,
                "report_id": verified.report_id,
                "report_digest": verified.report_digest,
                "export_status": verified.release_refusal_certificate.export_status,
                "production_export_authorized": verified.release_refusal_certificate.production_export_authorized,
            }
            sys.stdout.write(
                canonical_json_bytes(summary).decode("utf-8") + "\n"
            )
            return 0

        return 2
    except VipLabError as exc:
        sys.stderr.write(f"REFUSED: {exc.code}: {exc.message}\n")
        return 2
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2


if __name__ == "__main__":
    raise SystemExit(main())
