"""MEGA-14: Real End-to-End Synthetic Integration, CLI & Report (+ Stretch S2)."""

from vip_lab.mega08.gap_digest import MEGA_08_14_SPEC_VERSION
from vip_lab.mega14.cli import (
    EXIT_BLOCKED,
    EXIT_INVALID,
    EXIT_NOT_AUTHORIZED,
    EXIT_OK,
    main,
)
from vip_lab.mega14.orchestrator import run_end_to_end_synthetic_lab
from vip_lab.mega14.report import (
    E2E_REPORT_SCHEMA_VERSION,
    EndToEndLabReport,
    compute_e2e_report_digest,
    verify_e2e_lab_report,
)
from vip_lab.mega14.scenario import (
    ALLOWED_SCENARIO_MODES,
    E2E_SCENARIO_SCHEMA_VERSION,
    SyntheticLabScenario,
    default_single_arm_scenario,
    default_three_arm_scenario,
    load_e2e_scenario_file,
    parse_e2e_scenario_mapping,
)

__all__ = [
    "ALLOWED_SCENARIO_MODES",
    "E2E_REPORT_SCHEMA_VERSION",
    "E2E_SCENARIO_SCHEMA_VERSION",
    "EXIT_BLOCKED",
    "EXIT_INVALID",
    "EXIT_NOT_AUTHORIZED",
    "EXIT_OK",
    "MEGA_08_14_SPEC_VERSION",
    "EndToEndLabReport",
    "SyntheticLabScenario",
    "compute_e2e_report_digest",
    "default_single_arm_scenario",
    "default_three_arm_scenario",
    "load_e2e_scenario_file",
    "main",
    "parse_e2e_scenario_mapping",
    "run_end_to_end_synthetic_lab",
    "verify_e2e_lab_report",
]
