"""Task-7/8 checks for explicit-handoff N4B sealing."""
import ast
import inspect
from pathlib import Path
import subprocess
from typing import get_type_hints

import pytest

from gate0.feasibility import macos_stage_b_evidence_seal as seal
from gate0.feasibility import macos_stage_b_evidence_constants as contracts
from gate0.feasibility.macos_stage_b_evidence_constants import (
    N4AProductionResult, N4ATransientApplication, ReferenceClass, RetentionMode,
    N4ASealCapability, N4ASealHandoff, EvidenceDagError,
)
from tests.gate0.unit.evidence_dag_interface_manifest import INTERFACE_MANIFEST


SUCCESSOR_SPEC_BLOB = "d3d7a4611e375317e651049bceb345fe0d879744"


def _manifest_row(section, name):
    return next(row for row in INTERFACE_MANIFEST[section] if row["name"] == name)


def test_seal_api_accepts_only_s7_and_handoff():
    signature = inspect.signature(seal.seal_n4b)
    assert tuple(signature.parameters) == ("s7", "handoff")


def test_old_frozen_seal_signature_cannot_accept_new_handoff_contract():
    assert get_type_hints(seal.seal_n4b)["handoff"] is N4ASealHandoff
    legacy_capability = N4ASealCapability("c" * 64, object(), object(), object())
    with pytest.raises(EvidenceDagError, match="exact S7 and handoff types"):
        seal.seal_n4b(None, legacy_capability)


def test_sealer_has_no_compatibility_primitive_slot_access():
    tree = ast.parse(inspect.getsource(seal))
    assert not any(isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                   and node.slice.value == 5 for node in ast.walk(tree))


def test_downstream_task10_subject_remains_transient_application():
    result = _manifest_row("dataclasses", "N4AProductionResult")
    fields = {field["name"]: field["type"] for field in result["fields"]}
    assert fields["transient_application"] == "N4ATransientApplication"
    assert fields["n4b_handoff"] == "N4ASealHandoff"
    assert get_type_hints(N4AProductionResult)["transient_application"] is N4ATransientApplication
    n5 = next(row for row in INTERFACE_MANIFEST["callables"]
              if row["module"] == "macos_stage_b_evidence_s8"
              and row["name"] == "capture_and_evaluate_s8")
    assert n5["parameters"][0] == {
        "name": "application", "annotation": "N4ATransientApplication",
    }


def test_task11_p19_p20_and_measurement_only_keys_are_unchanged():
    assert tuple(member.value for member in ReferenceClass) == (
        "PATH_REFERENCE", "FILE_BLOB_REFERENCE", "COMMIT_OBJECT_REFERENCE",
        "AUTHORITY_DESIGN_RECORD_REFERENCE",
    )
    assert tuple(member.value for member in RetentionMode) == (
        "RETAINED_OBJECT", "RETAINED_SEAL_TIME_MEASUREMENT_ONLY",
    )
    assert contracts.MEASUREMENT_ONLY_DIGEST_KEYS == frozenset({
        "requirements_blob_sha256", "cms_signature_blob_sha256",
    })


def test_tasks12_13_14_16_s9_inventory_is_exact():
    result = _manifest_row("dataclasses", "SealResult")
    fields = {field["name"]: field["type"] for field in result["fields"]}
    assert fields["projection_members"] == "tuple[tuple[str, str], ...]"
    repository = Path(__file__).resolve().parents[3]
    successor_spec = subprocess.run(
        ("git", "cat-file", "blob", SUCCESSOR_SPEC_BLOB),
        cwd=repository, check=True, stdout=subprocess.PIPE, text=True,
    ).stdout
    section = successor_spec.split("## 3. Exact fixed member set\n", 1)[1].split(
        "\nThe exact `source_member_mapping` values are:", 1,
    )[0]
    expected_inventory = tuple(
        (columns[0].strip(" `"), columns[1].strip(" `"))
        for line in section.splitlines()
        if line.startswith("|")
        and (columns := [column.strip() for column in line.strip("|").split("|")])
        and len(columns) >= 3
        and columns[0].strip(" `") not in {"#", "Manifest member key", "---"}
        and not set(columns[0].strip(" `")) <= {"-", ":"}
    )
    assert INTERFACE_MANIFEST["successor_task10_compatibility"]["s9_inventory"] == expected_inventory


def test_task15_has_no_successor_behavior_delta():
    repository = Path(__file__).resolve().parents[3]
    successor_spec = subprocess.run(
        ("git", "cat-file", "blob", "d3d7a4611e375317e651049bceb345fe0d879744"),
        cwd=repository, check=True, stdout=subprocess.PIPE,
    ).stdout
    assert b"Task 15 has no behavior or authority change." in successor_spec
    # Task-15-owned files from the frozen predecessor plan must remain byte-identical
    # to accepted A05; this compares source/test inputs, not this candidate's metadata.
    task15_paths = (
        "scripts/stage-b-build-app.sh",
        "tests/gate0/unit/test_stage_b_evidence_build_boundary.py",
        ".gitignore",
    )
    for path in task15_paths:
        baseline_exists = subprocess.run(
            ("git", "cat-file", "-e", f"bf7e68e856cc64ddc5ca86be8172331320f77e74:{path}"),
            cwd=repository, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        current_exists = subprocess.run(
            ("git", "cat-file", "-e", f"HEAD:{path}"), cwd=repository,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        assert current_exists == baseline_exists, path
        if baseline_exists:
            baseline = subprocess.run(
                ("git", "rev-parse", f"bf7e68e856cc64ddc5ca86be8172331320f77e74:{path}"),
                cwd=repository, check=True, text=True, stdout=subprocess.PIPE,
            ).stdout.strip()
            current = subprocess.run(
                ("git", "rev-parse", f"HEAD:{path}"), cwd=repository, check=True,
                text=True, stdout=subprocess.PIPE,
            ).stdout.strip()
            assert current == baseline, path
    contract = INTERFACE_MANIFEST["successor_task10_compatibility"]
    assert contract["changed_downstream_tasks"] == (10, 11, 12, 13, 14, 16)
    assert 15 not in contract["changed_downstream_tasks"]
    assert contract["task15_behavior_delta"] is None
