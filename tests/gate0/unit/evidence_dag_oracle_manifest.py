"""Plan-owned, expectation-free N4a oracle requests and independent observers."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

from gate0.feasibility.macos_stage_b_evidence_constants import (
    OracleInspectionDomain, OracleInspectionMechanism, OracleExpectedResult, TestContractError,
)

@dataclass(frozen=True)
class OracleInspectionRequest:
    domain: OracleInspectionDomain
    surface_id: str
    production_paths: tuple[str, ...]
    mechanism: OracleInspectionMechanism
    forbidden_form: str

@dataclass(frozen=True)
class OracleInspectionExpectation:
    surface_id: str
    expected: OracleExpectedResult

@dataclass(frozen=True)
class OracleInspectionObservation:
    surface_id: str
    mechanism: OracleInspectionMechanism
    matches: tuple[str, ...]
    reachable_symbols: tuple[str, ...]
    import_resolution: tuple[str, ...]
    import_succeeded: bool | None

@dataclass(frozen=True)
class SyntheticSourceTree:
    files: tuple[tuple[str, bytes], ...]
    package_files: tuple[tuple[str, bytes], ...] = ()
    import_paths: tuple[str, ...] = ()

    def read(self, path: str) -> bytes | None:
        return dict(self.files).get(path, dict(self.package_files).get(path))

_REQUEST_DATA = [{'domain': 'A',
  'surface_id': 'A01',
  'production_paths': ['scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_SIGNATURE',
  'forbidden_form': 'CLI option or argparse destination matching '
                    'measurer|oracle|measurement_helper|measurement_strategy|measurement_callback'},
 {'domain': 'A',
  'surface_id': 'A02',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py'],
  'mechanism': 'AST_CALL',
  'forbidden_form': 'os.environ/getenv access whose key can select measurer/oracle/helper/strategy'},
 {'domain': 'A',
  'surface_id': 'A03',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py'],
  'mechanism': 'TEXT_SCHEMA',
  'forbidden_form': 'schema/dataclass field named '
                    'measurer|oracle|measurement_helper|measurement_strategy|callback_selector'},
 {'domain': 'A',
  'surface_id': 'A04',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py'],
  'mechanism': 'TEXT_SCHEMA',
  'forbidden_form': 'runtime-policy field/value selecting N4a measurer/oracle/helper'},
 {'domain': 'A',
  'surface_id': 'A05',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py'],
  'mechanism': 'TEXT_SCHEMA',
  'forbidden_form': 'ProducerSnapshotInputs or producer-authored field selecting measurer/oracle/helper'},
 {'domain': 'A',
  'surface_id': 'A06',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'scripts/stage-b-build-app.sh'],
  'mechanism': 'TEXT_SCHEMA',
  'forbidden_form': 'build/runtime-adapter config key selecting measurer/oracle/helper'},
 {'domain': 'A',
  'surface_id': 'A07',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_ASSIGNMENT',
  'forbidden_form': 'feature/config switch whose branch target is a measurement/oracle/helper callable'},
 {'domain': 'B',
  'surface_id': 'B01',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_boundary.py'],
  'mechanism': 'AST_SIGNATURE',
  'forbidden_form': 'measure_and_handoff_n4a/invoke_stage_b_build_app parameter named or annotated as '
                    'measurer|oracle|Callable helper'},
 {'domain': 'B',
  'surface_id': 'B02',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py'],
  'mechanism': 'AST_CONSTRUCTOR',
  'forbidden_form': 'constructor field/argument carrying callable measurer/oracle/helper'},
 {'domain': 'B',
  'surface_id': 'B03',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'CALL_REACHABILITY_GRAPH',
  'forbidden_form': 'production Callable/dependency-injection parameter capable of selecting N4a measurement '
                    'behavior'},
 {'domain': 'B',
  'surface_id': 'B04',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_CALL',
  'forbidden_form': 'setter API set_*measurer|set_*oracle|set_*measurement_helper'},
 {'domain': 'B',
  'surface_id': 'B05',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_CALL',
  'forbidden_form': 'mutator API mutating measurement/oracle/helper selection'},
 {'domain': 'B',
  'surface_id': 'B06',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_boundary.py'],
  'mechanism': 'AST_SIGNATURE',
  'forbidden_form': 'factory parameter accepting measurer/oracle/callback/strategy'},
 {'domain': 'B',
  'surface_id': 'B07',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_ASSIGNMENT',
  'forbidden_form': 'registry mapping key/value selecting measurer/oracle/helper'},
 {'domain': 'B',
  'surface_id': 'B08',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_ASSIGNMENT',
  'forbidden_form': 'plugin/provider map selecting measurement helper'},
 {'domain': 'B',
  'surface_id': 'B09',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'CALL_REACHABILITY_GRAPH',
  'forbidden_form': 'callback/hook parameter that can intercept N4a measurement'},
 {'domain': 'B',
  'surface_id': 'B10',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'CALL_REACHABILITY_GRAPH',
  'forbidden_form': 'strategy parameter/object selecting measurement implementation'},
 {'domain': 'B',
  'surface_id': 'B11',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_boundary.py'],
  'mechanism': 'CALL_REACHABILITY_GRAPH',
  'forbidden_form': 'second production-reachable measurer/helper API besides the fixed private leaf'},
 {'domain': 'B',
  'surface_id': 'B12',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_IMPORT',
  'forbidden_form': 'importlib/__import__/loader hook selecting measurement/oracle module'},
 {'domain': 'B',
  'surface_id': 'B13',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_ASSIGNMENT',
  'forbidden_form': 'mutable module global storing selectable measurer/oracle/helper callable'},
 {'domain': 'B',
  'surface_id': 'B14',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py'],
  'mechanism': 'TEXT_SCHEMA',
  'forbidden_form': 'generic configuration dataclass/dict field typed Callable or helper selector'},
 {'domain': 'B',
  'surface_id': 'B15',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_CALL',
  'forbidden_form': 'getattr/globals/locals/eval/exec dynamic dispatch selecting measurement/oracle/helper'},
 {'domain': 'B',
  'surface_id': 'B16',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_ASSIGNMENT',
  'forbidden_form': 'conditional/dict alias dispatch equivalent to a selector-bearing measurement call'},
 {'domain': 'C',
  'surface_id': 'C01',
  'production_paths': ['src/gate0/feasibility', 'scripts'],
  'mechanism': 'PATH_ABSENCE',
  'forbidden_form': 'evidence_dag_oracle_manifest.py or test oracle module beneath ordinary production '
                    'source root'},
 {'domain': 'C',
  'surface_id': 'C02',
  'production_paths': ['pyproject.toml', 'setup.py', 'setup.cfg', 'MANIFEST.in'],
  'mechanism': 'PACKAGE_MANIFEST',
  'forbidden_form': 'tests.gate0.unit.evidence_dag_oracle_manifest or evidence_dag_oracle_manifest'},
 {'domain': 'C',
  'surface_id': 'C03',
  'production_paths': ['requirements/gate0-macos-stage-a.lock'],
  'mechanism': 'DEPENDENCY_MANIFEST',
  'forbidden_form': 'test oracle/helper package or editable test path'},
 {'domain': 'C',
  'surface_id': 'C04',
  'production_paths': ['scripts/stage-b-evidence-dag.py'],
  'mechanism': 'AST_CALL',
  'forbidden_form': 'sys.path mutation adding repository tests/gate0/unit or repository root solely to '
                    'expose test oracle'},
 {'domain': 'C',
  'surface_id': 'C05',
  'production_paths': ['src/gate0/feasibility', 'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'IMPORT_RESOLUTION',
  'forbidden_form': 'ordinary production module-search resolution of '
                    'tests.gate0.unit.evidence_dag_oracle_manifest'},
 {'domain': 'C',
  'surface_id': 'C06',
  'production_paths': ['src/gate0/feasibility', 'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'IMPORT_RESOLUTION',
  'forbidden_form': 'ordinary production import tests.gate0.unit.evidence_dag_oracle_manifest'},
 {'domain': 'C',
  'surface_id': 'C07',
  'production_paths': ['src/gate0/feasibility/macos_stage_b_evidence_constants.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_macho.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_runtime.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_git.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_authority.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_snapshot.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_anchor.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_boundary.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_projection.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_seal.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_s8.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_references.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_retention.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_results.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_package.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_gate.py',
                       'src/gate0/feasibility/macos_stage_b_evidence_orchestrator.py',
                       'scripts/stage-b-evidence-dag.py'],
  'mechanism': 'REEXPORT_GRAPH',
  'forbidden_form': 'import/re-export/alias edge to tests.gate0.unit.evidence_dag_oracle_manifest or oracle '
                    'helper'}]
_EXPECTATION_DATA = [{'surface_id': 'A01', 'expected': 'ABSENT'},
 {'surface_id': 'A02', 'expected': 'ABSENT'},
 {'surface_id': 'A03', 'expected': 'ABSENT'},
 {'surface_id': 'A04', 'expected': 'ABSENT'},
 {'surface_id': 'A05', 'expected': 'ABSENT'},
 {'surface_id': 'A06', 'expected': 'ABSENT'},
 {'surface_id': 'A07', 'expected': 'ABSENT'},
 {'surface_id': 'B01', 'expected': 'ABSENT'},
 {'surface_id': 'B02', 'expected': 'ABSENT'},
 {'surface_id': 'B03', 'expected': 'ABSENT'},
 {'surface_id': 'B04', 'expected': 'ABSENT'},
 {'surface_id': 'B05', 'expected': 'ABSENT'},
 {'surface_id': 'B06', 'expected': 'ABSENT'},
 {'surface_id': 'B07', 'expected': 'ABSENT'},
 {'surface_id': 'B08', 'expected': 'ABSENT'},
 {'surface_id': 'B09', 'expected': 'ABSENT'},
 {'surface_id': 'B10', 'expected': 'ABSENT'},
 {'surface_id': 'B11', 'expected': 'ABSENT'},
 {'surface_id': 'B12', 'expected': 'ABSENT'},
 {'surface_id': 'B13', 'expected': 'ABSENT'},
 {'surface_id': 'B14', 'expected': 'ABSENT'},
 {'surface_id': 'B15', 'expected': 'ABSENT'},
 {'surface_id': 'B16', 'expected': 'ABSENT'},
 {'surface_id': 'C01', 'expected': 'ABSENT'},
 {'surface_id': 'C02', 'expected': 'ABSENT'},
 {'surface_id': 'C03', 'expected': 'ABSENT'},
 {'surface_id': 'C04', 'expected': 'ABSENT'},
 {'surface_id': 'C05', 'expected': 'IMPORT_FAILS'},
 {'surface_id': 'C06', 'expected': 'IMPORT_FAILS'},
 {'surface_id': 'C07', 'expected': 'ABSENT'}]
ORACLE_INSPECTION_REQUESTS = tuple(OracleInspectionRequest(
    OracleInspectionDomain[x["domain"]], x["surface_id"], tuple(x["production_paths"]),
    OracleInspectionMechanism[x["mechanism"]], x["forbidden_form"]
) for x in _REQUEST_DATA)
ORACLE_INSPECTION_EXPECTATIONS = tuple(OracleInspectionExpectation(
    x["surface_id"], OracleExpectedResult[x["expected"]]
) for x in _EXPECTATION_DATA)

_ROOT = Path(__file__).resolve().parents[3]
_SELECTOR = re.compile(r"measurer|oracle|measurement_helper|measurement_strategy|callback_selector", re.I)
_SELECTABLE_CALLABLE = re.compile(r"measurer|measurement_helper|measurement_strategy|callback_selector|oracle_(?:helper|measure|callable)", re.I)

def oracle_expectation_for(surface_id: str) -> OracleInspectionExpectation:
    rows = [x for x in ORACLE_INSPECTION_EXPECTATIONS if x.surface_id == surface_id]
    if len(rows) != 1:
        raise TestContractError(f"no unique oracle expectation for {surface_id}")
    return rows[0]

def _read_request_path(request: OracleInspectionRequest, path: str, tree: SyntheticSourceTree | None) -> bytes | None:
    if tree is not None:
        return tree.read(path)
    candidate = _ROOT / path
    try:
        if candidate.is_file():
            return candidate.read_bytes()
        return None
    except OSError as exc:
        raise TestContractError(f"oracle path read failed: {path}") from exc

def _all_text(request: OracleInspectionRequest, tree: SyntheticSourceTree | None) -> tuple[tuple[str, str], ...]:
    rows = []
    for path in request.production_paths:
        raw = _read_request_path(request, path, tree)
        if raw is None:
            continue
        try:
            rows.append((path, raw.decode("utf-8", "strict")))
        except UnicodeDecodeError:
            continue
    return tuple(rows)

def _ast_records(text: str):
    try:
        return ast.parse(text)
    except SyntaxError:
        return None

def _inspect(request: OracleInspectionRequest, tree: SyntheticSourceTree | None) -> OracleInspectionObservation:
    mechanism = request.mechanism
    matches: list[str] = []
    reachable: list[str] = []
    resolution: list[str] = []
    import_succeeded: bool | None = None
    rows = _all_text(request, tree)
    if mechanism is OracleInspectionMechanism.PATH_ABSENCE:
        matches.extend(path for path in request.production_paths if _read_request_path(request, path, tree) is not None)
    elif mechanism is OracleInspectionMechanism.PACKAGE_MANIFEST:
        for path, text in rows:
            try:
                document = tomllib.loads(text) if path.endswith(".toml") else {}
            except tomllib.TOMLDecodeError:
                continue
            serialized = repr(document).lower()
            if "tests.gate0.unit.evidence_dag_oracle_manifest" in serialized or "evidence_dag_oracle_manifest" in serialized:
                matches.append(f"{path}:oracle-package-reference")
    elif mechanism is OracleInspectionMechanism.DEPENDENCY_MANIFEST:
        for path, text in rows:
            for line_no, line in enumerate(text.splitlines(), 1):
                if re.search(r"(?:evidence[-_]dag[-_]oracle|test[-_]oracle|synthetic[-_]oracle)", line, re.I):
                    matches.append(f"{path}:{line_no}:oracle-dependency")
    elif mechanism is OracleInspectionMechanism.IMPORT_RESOLUTION:
        module = "tests.gate0.unit.evidence_dag_oracle_manifest"
        if tree is not None:
            candidate_paths = tuple(tree.import_paths)
            # Resolution is a path-order calculation; no production module is imported.
            found = next((p for p in candidate_paths if tree.read(p) is not None), None)
            import_succeeded = found is not None
            resolution.extend(candidate_paths)
            if found is not None:
                matches.append(f"{module}->{found}")
        else:
            import_succeeded = False
            resolution.extend(("src", "scripts"))
            for path, text in rows:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module == module:
                        import_succeeded = True
                        matches.append(f"{path}:{node.lineno}:{module}")
    elif mechanism is OracleInspectionMechanism.TEXT_SCHEMA:
        for path, text in rows:
            module = _ast_records(text)
            if module is None: continue
            for node in ast.walk(module):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    for child in ast.walk(node):
                        if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                            name, annotation = child.target.id, ast.unparse(child.annotation)
                            if _SELECTOR.search(name) and ("Callable" in annotation or annotation == "str"):
                                matches.append(f"{path}:{child.lineno}:schema-field:{name}")
    elif mechanism is OracleInspectionMechanism.CALL_REACHABILITY_GRAPH:
        functions: dict[str, list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]] = {}
        modules = []
        for path, text in rows:
            module = _ast_records(text)
            if module is None: continue
            modules.append((path, module))
            for node in ast.walk(module):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.setdefault(node.name, []).append((path, node))
        work = [name for name in functions if name in {"measure_and_handoff_n4a", "invoke_stage_b_build_app", "production_boundary"}]
        seen: set[tuple[str, str]] = set()
        while work:
            name = work.pop()
            for path, fn in functions.get(name, ()):
                marker = (path, name)
                if marker in seen: continue
                seen.add(marker)
                args = list(fn.args.posonlyargs) + list(fn.args.args) + list(fn.args.kwonlyargs)
                for arg in args:
                    annotation = ast.unparse(arg.annotation) if arg.annotation is not None else ""
                    if arg.arg.lower() in {"measurer", "oracle", "helper", "strategy", "callback"} or "Callable" in annotation:
                        matches.append(f"{path}:{fn.lineno}:reachable-selector-parameter:{arg.arg}")
                for node in ast.walk(fn):
                    if isinstance(node, ast.Call):
                        callee = node.func.id if isinstance(node.func, ast.Name) else None
                        if callee and _SELECTABLE_CALLABLE.search(callee):
                            matches.append(f"{path}:{node.lineno}:reachable-selector-call:{callee}")
                        if callee in functions and callee != name:
                            work.append(callee)
        reachable.extend(f"{path}:{name}" for path, name in sorted(seen))
        reached_paths = {path for path, _ in seen}
        for path, module in modules:
            if path not in reached_paths: continue
            for node in ast.walk(module):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imported = ",".join(a.name for a in node.names) if isinstance(node, ast.Import) else (node.module or "")
                    if _SELECTABLE_CALLABLE.search(imported):
                        matches.append(f"{path}:{node.lineno}:reachable-selector-import:{imported}")
    else:
        for path, text in rows:
            module = _ast_records(text)
            if module is None:
                continue
            if mechanism is OracleInspectionMechanism.AST_SIGNATURE:
                for node in ast.walk(module):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        args = list(node.args.posonlyargs) + list(node.args.args) if hasattr(node, "args") else []
                        for arg in args:
                            if _SELECTOR.search(arg.arg) or (arg.annotation is not None and _SELECTOR.search(ast.unparse(arg.annotation))):
                                matches.append(f"{path}:{node.lineno}:{node.name}({arg.arg})")
            elif mechanism is OracleInspectionMechanism.AST_CONSTRUCTOR:
                for node in ast.walk(module):
                    if isinstance(node, ast.Call) and any(
                        (isinstance(arg, ast.Name) and arg.id.lower() in {"measurer", "oracle", "helper"})
                        or (isinstance(arg, ast.Lambda) and _SELECTOR.search(ast.unparse(arg)))
                        for arg in node.args
                    ):
                        matches.append(f"{path}:{node.lineno}:constructor-selector")
            elif mechanism is OracleInspectionMechanism.AST_ASSIGNMENT:
                for node in ast.walk(module):
                    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                        names = [n.id for target in (node.targets if isinstance(node, ast.Assign) else [node.target]) for n in ast.walk(target) if isinstance(n, ast.Name)]
                        value = ast.unparse(node.value) if node.value is not None else ""
                        if request.surface_id == "A07":
                            selected = bool(_SELECTABLE_CALLABLE.search(value)) and bool(re.search(r"if |match |registry|feature|strategy|select|measure", value, re.I))
                        elif request.surface_id in {"B07", "B08"}:
                            selected = bool(re.search(r"registry|plugin|provider|map", " ".join(names), re.I)) and bool(_SELECTABLE_CALLABLE.search(value))
                        elif request.surface_id == "B13":
                            selected = any(_SELECTOR.search(name) for name in names) and bool(re.search(r"=\s*(?:None|lambda|[A-Za-z_][\w.]*)", value))
                        elif request.surface_id == "B16":
                            selected = bool(_SELECTABLE_CALLABLE.search(value)) and (
                                isinstance(node.value, (ast.IfExp, ast.Dict))
                                or bool(re.search(r"\b(?:getattr|globals|locals|eval|exec)\b", value))
                            )
                        else:
                            selected = any(_SELECTOR.search(name) for name in names) or bool(_SELECTOR.search(value))
                        if selected:
                            matches.append(f"{path}:{node.lineno}:assignment-selector")
            elif mechanism is OracleInspectionMechanism.AST_CALL:
                for node in ast.walk(module):
                    if isinstance(node, ast.Call) and _SELECTOR.search(ast.unparse(node.func)):
                        matches.append(f"{path}:{node.lineno}:call:{ast.unparse(node.func)}")
            elif mechanism is OracleInspectionMechanism.AST_IMPORT:
                for node in ast.walk(module):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        name = ",".join(a.name for a in node.names) if isinstance(node, ast.Import) else (node.module or "")
                        if _SELECTOR.search(name) or name in {"importlib", "builtins"}:
                            matches.append(f"{path}:{node.lineno}:import:{name}")
            elif mechanism is OracleInspectionMechanism.REEXPORT_GRAPH:
                for node in ast.walk(module):
                    if isinstance(node, ast.ImportFrom) and (node.module or "").endswith("oracle"):
                        reachable.extend(a.asname or a.name for a in node.names)
                        matches.append(f"{path}:{node.lineno}:reexport:{node.module}")
    return OracleInspectionObservation(request.surface_id, mechanism, tuple(sorted(set(matches))),
                                       tuple(sorted(set(reachable))), tuple(resolution), import_succeeded)

def inspect_oracle_request(request: OracleInspectionRequest) -> OracleInspectionObservation:
    if type(request) is not OracleInspectionRequest:
        raise TestContractError("oracle inspector requires exact request type")
    return _inspect(request, None)

def compare_oracle_observation(observation: OracleInspectionObservation,
                               expectation: OracleInspectionExpectation) -> bool:
    if type(observation) is not OracleInspectionObservation or type(expectation) is not OracleInspectionExpectation:
        raise TestContractError("oracle comparator requires exact records")
    if observation.surface_id != expectation.surface_id:
        raise TestContractError("oracle observation/expectation surfaces differ")
    if expectation.expected is OracleExpectedResult.ABSENT:
        return not observation.matches
    return observation.import_succeeded is False

def _positive_fixture(mechanism: OracleInspectionMechanism) -> tuple[str, bytes, tuple[str, ...]]:
    snippets = {
        OracleInspectionMechanism.AST_SIGNATURE: ("synthetic.py", b"def f(measurer): return measurer(b'x')\n", ()),
        OracleInspectionMechanism.AST_CALL: ("synthetic.py", b"def f(): return oracle.measure()\n", ()),
        OracleInspectionMechanism.TEXT_SCHEMA: ("synthetic.py", b"class Config:\n    measurement_strategy: str\n", ()),
        OracleInspectionMechanism.AST_ASSIGNMENT: ("synthetic.py", b"MEASURER = oracle_measure if use_oracle else fixed_measure\n", ()),
        OracleInspectionMechanism.AST_CONSTRUCTOR: ("synthetic.py", b"def f(): return Boundary(measurer)\n", ()),
        OracleInspectionMechanism.AST_IMPORT: ("synthetic.py", b"import importlib\n", ()),
        OracleInspectionMechanism.PATH_ABSENCE: ("synthetic_prod/test_oracle.py", b"def measure(x): return x\n", ()),
        OracleInspectionMechanism.PACKAGE_MANIFEST: ("pyproject.toml", b"[tool.setuptools.package-data]\n'evidence_dag_oracle_manifest' = ['*']\n", ()),
        OracleInspectionMechanism.DEPENDENCY_MANIFEST: ("requirements.txt", b"test-oracle @ file:///synthetic/test-oracle\n", ()),
        OracleInspectionMechanism.IMPORT_RESOLUTION: ("synthetic_test_oracle/test_oracle.py", b"", ("synthetic_test_oracle/test_oracle.py",)),
        OracleInspectionMechanism.REEXPORT_GRAPH: ("synthetic.py", b"from test_oracle import measure as measure\n", ()),
        OracleInspectionMechanism.CALL_REACHABILITY_GRAPH: ("synthetic.py", b"def measure_and_handoff_n4a(payload, strategy):\n    return select_helper(payload)\ndef select_helper(payload):\n    return strategy(payload)\n", ()),
    }
    return snippets[mechanism]

def positive_falsifier_for(mechanism: OracleInspectionMechanism) -> tuple[OracleInspectionRequest, SyntheticSourceTree]:
    requests = [x for x in ORACLE_INSPECTION_REQUESTS if x.mechanism is mechanism]
    if not requests:
        raise TestContractError(f"no request for mechanism {mechanism}")
    path, raw, import_paths = _positive_fixture(mechanism)
    base = requests[0]
    request = OracleInspectionRequest(base.domain, f"POSITIVE-{mechanism.value}", (path,), mechanism, base.forbidden_form)
    package = ((path, raw),) if path.endswith((".toml", ".txt")) else ()
    files = () if package else ((path, raw),)
    return request, SyntheticSourceTree(files, package, import_paths)

def inspect_oracle_request_against_tree(request: OracleInspectionRequest,
                                        tree: SyntheticSourceTree) -> OracleInspectionObservation:
    if type(request) is not OracleInspectionRequest or type(tree) is not SyntheticSourceTree:
        raise TestContractError("synthetic oracle inspection requires exact inputs")
    return _inspect(request, tree)

def observation_has_forbidden_match(observation: OracleInspectionObservation) -> bool:
    return bool(observation.matches)

def oracle_echo_inspector_falsifier() -> bool:
    def constant_absent(request: OracleInspectionRequest) -> OracleInspectionObservation:
        return OracleInspectionObservation(request.surface_id, request.mechanism, (), (), (), None)
    # The comparison truth includes two IMPORT_FAILS claims, so a constant
    # absence echo cannot satisfy the complete independent comparison.
    return all(compare_oracle_observation(constant_absent(request), oracle_expectation_for(request.surface_id))
               for request in ORACLE_INSPECTION_REQUESTS)
