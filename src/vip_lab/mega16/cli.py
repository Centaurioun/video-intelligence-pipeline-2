from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping, Sequence

from vip_lab.common import (
    FORBIDDEN_EXTERNAL_AUTHORITY_KEYS,
    NOT_OBSERVED,
    VipLabError,
    canonical_json_dumps,
    load_bounded_json_file,
)
from vip_lab.mega16.qc_requirements import validate_qc_claim_or_refuse
from vip_lab.mega16.release_refusal import (
    Mega1516OfflineBundle,
    run_mega15_16_offline_pipeline,
    verify_mega15_16_offline_bundle,
)

FORBIDDEN_CLI_FLAGS = frozenset(
    {
        "--real",
        "--render",
        "--export",
        "--provider",
        "--download",
        "--upload",
        "--archive",
        "--model-weights",
        "--production",
        "--ffmpeg",
        "--ffprobe",
    }
)

FORBIDDEN_URL_PREFIXES = (
    "http://",
    "https://",
    "s3://",
    "gs://",
    "gdrive://",
    "file://",
)


def _check_forbidden_tokens(argv: Sequence[str]) -> None:
    for token in argv:
        head = token.split("=", 1)[0]
        if head in FORBIDDEN_CLI_FLAGS:
            raise VipLabError(f"Forbidden real/render/export/network CLI flag rejected: {head}")
        lowered = token.lower()
        for prefix in FORBIDDEN_URL_PREFIXES:
            if lowered.startswith(prefix) or f"={prefix}" in lowered:
                raise VipLabError(f"External or file URL argument is prohibited in synthetic CLI: {token}")


def _validate_untrusted_input_mapping(payload: Mapping[str, Any]) -> None:
    forbidden_present = sorted(
        k for k in FORBIDDEN_EXTERNAL_AUTHORITY_KEYS if bool(payload.get(k))
    )
    if forbidden_present:
        raise VipLabError(f"Untrusted input contains forbidden authority keys: {forbidden_present}")
    if payload.get("source_pts_evidence_state") not in (None, NOT_OBSERVED):
        raise VipLabError("Untrusted input claims measured source_pts_evidence_state.")
    if payload.get("real_human_decision_state") not in (None, NOT_OBSERVED):
        raise VipLabError("Untrusted input claims real_human_decision_state.")
    validate_qc_claim_or_refuse(payload)


def main(argv: Sequence[str] | None = None) -> int:
    args_list = list(argv) if argv is not None else []
    try:
        _check_forbidden_tokens(args_list)
    except VipLabError:
        return 2

    parser = argparse.ArgumentParser(
        prog="vip-lab-mega16",
        description="MEGA-15/16 synthetic offline Gate-3 preparation and export-refusal runner",
        add_help=True,
    )
    parser.add_argument(
        "--mode",
        choices=("three_arm", "single_arm"),
        default="three_arm",
        help="Synthetic scenario mode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to write canonical JSON bundle report",
    )
    parser.add_argument(
        "--verify",
        type=str,
        default=None,
        help="Optional path to verify an existing Mega1516OfflineBundle JSON file",
    )
    parser.add_argument(
        "--check-input",
        type=str,
        default=None,
        help="Optional path to validate an untrusted input JSON against authority/measurement refusal rules",
    )

    try:
        parsed = parser.parse_args(args_list)
        if parsed.check_input is not None:
            raw_input = load_bounded_json_file(Path(parsed.check_input))
            if not isinstance(raw_input, Mapping):
                raise VipLabError("Input JSON must be an object.")
            _validate_untrusted_input_mapping(raw_input)
            return 0

        if parsed.verify is not None:
            raw_bundle = load_bounded_json_file(Path(parsed.verify))
            if not isinstance(raw_bundle, Mapping):
                raise VipLabError("Bundle JSON must be an object.")
            bundle = Mega1516OfflineBundle.from_dict(raw_bundle)
            verify_mega15_16_offline_bundle(bundle)
            return 0

        bundle = run_mega15_16_offline_pipeline(scenario_mode=parsed.mode)
        verify_mega15_16_offline_bundle(bundle)
        if parsed.output is not None:
            out_path = Path(parsed.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(canonical_json_dumps(bundle.to_dict()), encoding="utf-8")
        return 0
    except (VipLabError, SystemExit, Exception):
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
