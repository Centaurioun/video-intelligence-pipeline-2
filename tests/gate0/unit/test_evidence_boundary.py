"""N4a exact-instance boundary and expectation-free oracle regressions."""
from __future__ import annotations

from dataclasses import fields, replace
import ast
import copy
import gc
import hashlib
import importlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from types import ModuleType
from typing import get_type_hints
import weakref

import pytest

from gate0.feasibility.macos_stage_b_evidence_constants import (
    AnchoredS1Handle, CodeDirectoryIdentity, FrozenArtifact, N4ABoundaryPrimitive,
    N4AProductionResult,
    N4ASealCapability, N4ASealHandoff, N4ATransientApplication,
    OracleInspectionMechanism, SignedImageProjection, VerifiedRepositoryContext,
    VerifierOwnedBuildContext, VerifierOwnedSealedDestination,
    VerifierOwnedSigningIdentity,
)
from gate0.feasibility import macos_stage_b_evidence_anchor as anchor_mod
from gate0.feasibility import macos_stage_b_evidence_constants as constants_mod
from gate0.feasibility import macos_stage_b_evidence_git as git_mod
from gate0.feasibility import macos_stage_b_evidence_snapshot as snapshot_mod
from gate0.feasibility.macos_stage_b_evidence_authority import derive_generation_identity
from gate0.feasibility.macos_stage_b_evidence_constants import (
    AuthorityTuple, EvidenceDagError, EvidenceFailureCode, S7AnchorCreateResult,
)
from tests.gate0.unit.evidence_dag_oracle_manifest import (
    ORACLE_INSPECTION_REQUESTS, compare_oracle_observation,
    inspect_oracle_request, oracle_expectation_for, oracle_echo_inspector_falsifier,
    positive_falsifier_for, inspect_oracle_request_against_tree,
    observation_has_forbidden_match,
)
from tests.gate0.unit.evidence_dag_interface_manifest import INTERFACE_MANIFEST
from tests.gate0.unit.evidence_dag_fixtures import write_capture_bundle


def _boundary():
    spec = importlib.util.find_spec("gate0.feasibility.macos_stage_b_evidence_boundary")
    assert spec is not None, "N4a verifier boundary module is not implemented"
    return importlib.import_module("gate0.feasibility.macos_stage_b_evidence_boundary")


@pytest.fixture
def n4a_lineage(tmp_path, monkeypatch):
    """All Git and boundary material is confined to a fresh synthetic temp repo."""
    boundary = _boundary()
    root = tmp_path / "repo"
    root.mkdir()
    env = {**__import__("os").environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": __import__("os").devnull,
           "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
    def git(*args, input=None):
        return subprocess.run(("git", *args), cwd=root, env=env, input=input, check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
    git("init", "-q")
    # Repo-local identity keeps anchor subprocesses hermetic: the anchor runs Git
    # with a scrubbed env, so host/user identity auto-detection must not be needed.
    git("config", "user.name", "test")
    git("config", "user.email", "test@example.invalid")
    git("checkout", "-q", "-b", "main")
    (root / "controller.json").write_bytes(b"{}")
    git("add", "controller.json")
    git("commit", "-q", "-m", "base")
    base = git("rev-parse", "HEAD")
    blob = git("hash-object", "controller.json")
    authority = AuthorityTuple(base, blob, blob, blob, 1)
    generation = derive_generation_identity(authority)
    roots = {f"roots.{name}": f"/synthetic/{name}" for name in
             ("worktree", "worktree_src", "python", "python_runtime", "model", "synthetic", "ffmpeg", "ffprobe", "output")}
    s1data = json.dumps({"roots": roots, "tool_dependency_roots": [], "python_dependency_roots": []},
                        sort_keys=True, separators=(",", ":")).encode()
    s1 = FrozenArtifact("S1", "S1.json", s1data, hashlib.sha256(s1data).hexdigest(), len(s1data))
    s2 = snapshot_mod.render_s2_from_s1(s1)
    s3data = b"{}"
    s3 = FrozenArtifact("S3", "S3.json", s3data, hashlib.sha256(s3data).hexdigest(), len(s3data))
    s4data = b"{}"
    s4 = FrozenArtifact("S4", "S4.json", s4data, hashlib.sha256(s4data).hexdigest(), len(s4data))
    artifacts = (s1, s2, s3, s4)
    monkeypatch.setattr(git_mod, "_discover_repository_root_from_module_location", lambda: root)
    anchor = anchor_mod.create_s7_anchor(base, artifacts)
    context = git_mod.verify_repository_context(authority, anchor.commit_sha)
    anchored_s1 = anchor_mod.resolve_anchored_s1(context, anchor)
    build_context = boundary._create_verifier_owned_build_context(context, anchor)
    return {"root": root, "authority": authority, "generation": generation, "anchor": anchor,
            "context": context, "s1": s1, "s2": s2, "anchored_s1": anchored_s1,
            "build_context": build_context}


@pytest.fixture
def capture_registered(n4a_lineage, monkeypatch, request):
    """Register one completed synthetic app and retain the observed I/O trace."""
    boundary = _boundary()
    trace = {
        "events": [], "reads": [], "origin_fds": [], "closed_origin_fds": [],
        "registry_fs_violations": [], "expected": None,
    }
    original_register = boundary._register
    original_lock = boundary._REGISTRY_LOCK
    original_open = os.open
    original_read = os.read
    original_close = os.close

    class TrackedLock:
        def __init__(self):
            self._lock = threading.Lock()
            self._owner = threading.local()

        def __enter__(self):
            self._lock.acquire()
            self._owner.held = True
            return self

        def __exit__(self, *_):
            self._owner.held = False
            self._lock.release()

        def acquire(self, *args, **kwargs):
            acquired = self._lock.acquire(*args, **kwargs)
            if acquired:
                self._owner.held = True
            return acquired

        def release(self):
            self._owner.held = False
            self._lock.release()

        def held_by_current_thread(self):
            return getattr(self._owner, "held", False)

    tracked_lock = TrackedLock()

    def traced_fs_call(name, original):
        def call(*args, **kwargs):
            if tracked_lock.held_by_current_thread():
                trace["registry_fs_violations"].append(name)
            return original(*args, **kwargs)
        return call

    def record_register(handle, context, generation, kind, *args, **kwargs):
        original_register(handle, context, generation, kind, *args, **kwargs)
        if kind == "transient-app":
            trace["events"].append(("metadata-registration", handle))

    def traced_open(path, flags, *args, **kwargs):
        fd = original_open(path, flags, *args, **kwargs)
        if kwargs.get("dir_fd") is not None or path == n4a_lineage["root"]:
            trace["origin_fds"].append(fd)
            trace["events"].append(("graph-open", path, fd))
        return fd

    def traced_read(fd, size):
        trace["reads"].append(fd)
        return original_read(fd, size)

    def traced_close(fd):
        original_close(fd)
        if fd in trace["origin_fds"]:
            trace["closed_origin_fds"].append(fd)

    def fake_process(s2, build_context, private_s2_file, env):
        trace["events"].append(("producer-start", build_context.sealed_destination.application_path))
        callspec = getattr(request.node, "callspec", None)
        failure = callspec.params.get("failure", "") if callspec is not None else ""
        wrong_blob_magic = None
        if failure.startswith("wrong_blob_magic_"):
            slot_type = int(failure.rsplit("_", 1)[1])
            wrong_magic, special_slot = {
                2: (0xFADE7171, 2), 5: (0xFADE0C01, 5),
                7: (0xFADE0C01, 7), 0x10000: (0xFADE0C01, None),
            }[slot_type]
            wrong_blob_magic = (slot_type, wrong_magic, special_slot)
        trace["expected"] = write_capture_bundle(
            build_context.sealed_destination.application_path,
            wrong_blob_magic=wrong_blob_magic,
        )
        trace["events"].append(("producer-complete", build_context.sealed_destination.application_path))
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    monkeypatch.setattr(boundary, "_register", record_register)
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    monkeypatch.setattr(boundary, "_REGISTRY_LOCK", tracked_lock)
    open_wrapper = traced_fs_call("open", traced_open)
    monkeypatch.setattr(os, "read", traced_fs_call("read", traced_read))
    stat_wrapper = traced_fs_call("stat", os.stat)
    monkeypatch.setattr(os, "open", open_wrapper)
    monkeypatch.setattr(os, "stat", stat_wrapper)
    monkeypatch.setattr(os, "fstat", traced_fs_call("fstat", os.fstat))
    monkeypatch.setattr(os, "close", traced_fs_call("close", traced_close))
    monkeypatch.setattr(os, "supports_dir_fd", set(os.supports_dir_fd) | {open_wrapper, stat_wrapper})
    monkeypatch.setattr(os, "supports_follow_symlinks", set(os.supports_follow_symlinks) | {stat_wrapper})
    application = boundary.invoke_stage_b_build_app(
        n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    bindings = getattr(boundary, "_CAPTURE_BINDINGS", {})
    binding = next((value for key, value in bindings.items()
                    if getattr(value, "application", None) is application), None)
    def release_unconsumed_graph():
        if (binding is None or binding.session is None or binding.session.released
                or binding.session.release_attempted):
            return
        boundary._refuse_capture(binding, "synthetic test fixture terminal cleanup")
        from gate0.feasibility import macos_stage_b_evidence_projection as projection
        projection._release_origin_graph(binding.session)
    request.addfinalizer(release_unconsumed_graph)
    return {
        **n4a_lineage,
        "boundary": boundary,
        "application": application,
        "binding": binding,
        "trace": trace,
        "expected": trace["expected"],
        "original_registry_lock_type": type(original_lock),
    }


def test_n4a_retained_primitive_exactly_five_fields():
    assert tuple(f.name for f in fields(N4ABoundaryPrimitive)) == (
        "format", "renderer_input_sha256", "renderer_input_octets",
        "signer_entitlements_sha256", "signer_entitlements_octets",
    )
    assert N4ABoundaryPrimitive.__dataclass_params__.frozen


def test_n4a_result_legacy_fields_and_additive_handoff_are_exact():
    assert tuple((field.name, get_type_hints(N4AProductionResult)[field.name])
                 for field in fields(N4AProductionResult)) == (
        ("primitive", N4ABoundaryPrimitive),
        ("seal_capability", N4ASealCapability),
        ("transient_application", N4ATransientApplication),
        ("renderer_output_s2", FrozenArtifact),
        ("n4b_handoff", N4ASealHandoff),
    )
    assert N4AProductionResult.__dataclass_params__.frozen is True


def test_successor_projection_and_handoff_dataclass_fields_are_exact():
    expected = {
        "CodeDirectoryIdentity": (
            ("sha256", str),
            ("code_limit", int),
            ("page_size", int),
            ("code_slot_sha256", tuple[str, ...]),
            ("special_slot_sha256", tuple[tuple[int, str | None], ...]),
        ),
        "SignedImageProjection": (
            ("executable_code_region_bytes", bytes),
            ("info_plist_bytes", bytes),
            ("code_resources_bytes", bytes),
            ("superblob_index_bytes", bytes),
            ("code_directory_bytes", bytes),
            ("entitlements_blob_bytes", bytes),
            ("der_entitlements_blob_bytes", bytes),
            ("requirements_blob_sha256", str),
            ("cms_signature_blob_sha256", str),
            ("special_slot_state", tuple[tuple[int, bytes], ...]),
            ("signing_time_stable_code_directory_identity", None),
            ("canonical_identity_json_bytes", bytes),
        ),
        "VerifiedSignedImageProjectionSource": (
            ("source_application", N4ATransientApplication),
            ("generation_identity", str),
            ("repository_context", VerifiedRepositoryContext),
            ("executable_code_region_bytes", bytes),
            ("info_plist_bytes", bytes),
            ("code_resources_bytes", bytes),
            ("superblob_index_bytes", bytes),
            ("code_directory_bytes", bytes),
            ("entitlements_blob_bytes", bytes),
            ("der_entitlements_blob_bytes", bytes),
            ("requirements_blob_sha256", str),
            ("cms_signature_blob_sha256", str),
            ("special_slot_state", tuple[tuple[int, bytes], ...]),
            ("code_directory_identity", None),
            ("_capture_registration", object),
        ),
        "N4ASealHandoff": (
            ("measured_primitive", N4ABoundaryPrimitive),
            ("capability", N4ASealCapability),
            ("projection", None),
            ("source_application", N4ATransientApplication),
        ),
    }
    successor_types = {
        name: getattr(constants_mod, name, None)
        for name in expected
    }
    assert all(successor_types.values()), (
        "missing successor dataclasses: "
        + ", ".join(name for name, value in successor_types.items() if value is None)
    )
    expected["SignedImageProjection"] = tuple(
        (name, successor_types["CodeDirectoryIdentity"] if annotation is None else annotation)
        for name, annotation in expected["SignedImageProjection"]
    )
    expected["VerifiedSignedImageProjectionSource"] = tuple(
        (name, successor_types["CodeDirectoryIdentity"] if annotation is None else annotation)
        for name, annotation in expected["VerifiedSignedImageProjectionSource"]
    )
    expected["N4ASealHandoff"] = tuple(
        (name, successor_types["SignedImageProjection"] if annotation is None else annotation)
        for name, annotation in expected["N4ASealHandoff"]
    )
    for name, expected_fields in expected.items():
        value_type = successor_types[name]
        type_hints = get_type_hints(value_type)
        assert tuple((field.name, type_hints[field.name]) for field in fields(value_type)) == expected_fields
        assert value_type.__dataclass_params__.frozen is True


def test_successor_interface_manifest_matches_frozen_spec():
    expected = {
        "CodeDirectoryIdentity": {
            "module": "macos_stage_b_evidence_constants",
            "name": "CodeDirectoryIdentity",
            "fields": [
                {"name": "sha256", "type": "str"},
                {"name": "code_limit", "type": "int"},
                {"name": "page_size", "type": "int"},
                {"name": "code_slot_sha256", "type": "tuple[str, ...]"},
                {"name": "special_slot_sha256", "type": "tuple[tuple[int, str | None], ...]"},
            ],
            "frozen": True,
        },
        "SignedImageProjection": {
            "module": "macos_stage_b_evidence_constants",
            "name": "SignedImageProjection",
            "fields": [
                {"name": "executable_code_region_bytes", "type": "bytes"},
                {"name": "info_plist_bytes", "type": "bytes"},
                {"name": "code_resources_bytes", "type": "bytes"},
                {"name": "superblob_index_bytes", "type": "bytes"},
                {"name": "code_directory_bytes", "type": "bytes"},
                {"name": "entitlements_blob_bytes", "type": "bytes"},
                {"name": "der_entitlements_blob_bytes", "type": "bytes"},
                {"name": "requirements_blob_sha256", "type": "str"},
                {"name": "cms_signature_blob_sha256", "type": "str"},
                {"name": "special_slot_state", "type": "tuple[tuple[int, bytes], ...]"},
                {"name": "signing_time_stable_code_directory_identity", "type": "CodeDirectoryIdentity"},
                {"name": "canonical_identity_json_bytes", "type": "bytes"},
            ],
            "frozen": True,
        },
        "VerifiedSignedImageProjectionSource": {
            "module": "macos_stage_b_evidence_constants",
            "name": "VerifiedSignedImageProjectionSource",
            "fields": [
                {"name": "source_application", "type": "N4ATransientApplication"},
                {"name": "generation_identity", "type": "str"},
                {"name": "repository_context", "type": "VerifiedRepositoryContext"},
                {"name": "executable_code_region_bytes", "type": "bytes"},
                {"name": "info_plist_bytes", "type": "bytes"},
                {"name": "code_resources_bytes", "type": "bytes"},
                {"name": "superblob_index_bytes", "type": "bytes"},
                {"name": "code_directory_bytes", "type": "bytes"},
                {"name": "entitlements_blob_bytes", "type": "bytes"},
                {"name": "der_entitlements_blob_bytes", "type": "bytes"},
                {"name": "requirements_blob_sha256", "type": "str"},
                {"name": "cms_signature_blob_sha256", "type": "str"},
                {"name": "special_slot_state", "type": "tuple[tuple[int, bytes], ...]"},
                {"name": "code_directory_identity", "type": "CodeDirectoryIdentity"},
                {"name": "_capture_registration", "type": "object"},
            ],
            "frozen": True,
        },
        "N4AProductionResult": {
            "module": "macos_stage_b_evidence_constants",
            "name": "N4AProductionResult",
            "fields": [
                {"name": "primitive", "type": "N4ABoundaryPrimitive"},
                {"name": "seal_capability", "type": "N4ASealCapability"},
                {"name": "transient_application", "type": "N4ATransientApplication"},
                {"name": "renderer_output_s2", "type": "FrozenArtifact"},
                {"name": "n4b_handoff", "type": "N4ASealHandoff"},
            ],
            "frozen": True,
        },
        "N4ASealHandoff": {
            "module": "macos_stage_b_evidence_constants",
            "name": "N4ASealHandoff",
            "fields": [
                {"name": "measured_primitive", "type": "N4ABoundaryPrimitive"},
                {"name": "capability", "type": "N4ASealCapability"},
                {"name": "projection", "type": "SignedImageProjection"},
                {"name": "source_application", "type": "N4ATransientApplication"},
            ],
            "frozen": True,
        },
    }
    rows = {
        row["name"]: row
        for row in INTERFACE_MANIFEST["dataclasses"]
        if row["name"] in expected
    }
    assert rows == expected


def _direct_n4a_handoff(boundary, *, generation="c" * 64):
    context = VerifiedRepositoryContext(
        Path("/synthetic/repo"), Path("/synthetic/repo/.git"), "a" * 40,
        "b" * 40, generation, 1, 2, object(),
    )
    primitive = N4ABoundaryPrimitive(
        "N4A_BOUNDARY_V1", "1" * 64, 1, "2" * 64, 2,
    )
    capability = N4ASealCapability(
        generation, context._registration_token, object(), object(),
    )
    application = N4ATransientApplication(
        generation, Path("/synthetic/repo/.stage-b-build") / generation
        / "StageBSandboxRunner.app",
        context._registration_token, object(), object(),
    )
    identity = CodeDirectoryIdentity(
        "3" * 64, 0, 4096, (), tuple((slot, None) for slot in range(-1, -8, -1)),
    )
    projection = SignedImageProjection(
        b"code", b"plist", b"resources", b"index", b"directory",
        b"entitlements", b"der-entitlements", "4" * 64, "5" * 64,
        tuple((slot, b"") for slot in range(-1, -8, -1)), identity, b"{}",
    )
    handoff = N4ASealHandoff(primitive, capability, projection, application)
    boundary._register(
        application, context, generation, "transient-app",
        lifecycle_token=application._lifecycle_token,
    )
    boundary._register(
        capability, context, generation, "seal-capability",
        primitive=primitive, lifecycle_token=capability._lifecycle_token,
    )
    return context, primitive, capability, handoff


def test_n4a_registry_lock_is_module_level_nonreentrant_thread_lock():
    boundary = _boundary()
    assert type(boundary._REGISTRY_LOCK) is type(threading.Lock())
    assert boundary._REGISTRY_LOCK.acquire(blocking=False)
    try:
        assert not boundary._REGISTRY_LOCK.acquire(blocking=False)
    finally:
        boundary._REGISTRY_LOCK.release()
    tree = ast.parse(inspect.getsource(boundary))
    creations = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and any(
            isinstance(target, ast.Name) and target.id == "_REGISTRY_LOCK"
            for target in (
                node.targets if isinstance(node, ast.Assign) else (node.target,)
            )
        )
    ]
    assert len(creations) == 1
    value = creations[0].value
    assert isinstance(value, ast.Call)
    assert isinstance(value.func, ast.Attribute)
    assert isinstance(value.func.value, ast.Name)
    assert (value.func.value.id, value.func.attr) == ("threading", "Lock")


def test_all_registry_access_sites_are_lock_guarded():
    boundary = _boundary()
    tree = ast.parse(inspect.getsource(boundary))
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }

    def is_registry_access(node):
        parent = parents.get(node)
        return (
            isinstance(node, ast.Name)
            and node.id == "_REGISTRY"
            and not (
                isinstance(parent, ast.AnnAssign)
                and parent.target is node
            )
        )

    def is_guarded(node):
        parent = parents.get(node)
        while parent is not None:
            if isinstance(parent, ast.With) and any(
                isinstance(item.context_expr, ast.Name)
                and item.context_expr.id == "_REGISTRY_LOCK"
                for item in parent.items
            ):
                return True
            parent = parents.get(parent)
        return False

    accesses = [node for node in ast.walk(tree) if is_registry_access(node)]
    assert accesses
    assert all(is_guarded(node) for node in accesses)


def test_handoff_registration_uses_exact_weakref_and_lifecycle_token():
    boundary = _boundary()
    context, primitive, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    with boundary._REGISTRY_LOCK:
        record = boundary._REGISTRY[id(capability)]
    registered_ref, registered_token = record[6]
    assert isinstance(registered_ref, weakref.ReferenceType)
    assert registered_ref() is handoff
    assert registered_token is record[7] is capability._lifecycle_token
    assert record[5] is primitive
    assert record[1] is context


def test_registered_handoff_copy_does_not_claim_capability():
    boundary = _boundary()
    context, _, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="n4b_seal", handoff=copy.copy(handoff),
        )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None


def test_registered_value_equal_handoff_refuses_without_consuming_original():
    boundary = _boundary()
    context, _, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    equal_handoff = replace(handoff)
    assert equal_handoff == handoff and equal_handoff is not handoff
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="n4b_seal", handoff=equal_handoff,
        )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None


def test_dead_registered_handoff_refuses_without_consuming_capability():
    boundary = _boundary()
    context, primitive, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    handoff_values = tuple(getattr(handoff, field.name) for field in fields(handoff))
    registered_ref = weakref.ref(handoff)
    del handoff
    gc.collect()
    assert registered_ref() is None
    reconstructed = N4ASealHandoff(*handoff_values)
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="n4b_seal", handoff=reconstructed,
        )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="legacy_consume",
    ) is primitive


def test_stale_generation_handoff_refuses_without_consuming_new_capability():
    boundary = _boundary()
    old_context, _, old_capability, old_handoff = _direct_n4a_handoff(
        boundary, generation="c" * 64,
    )
    new_context, _, new_capability, new_handoff = _direct_n4a_handoff(
        boundary, generation="d" * 64,
    )
    boundary._bind_n4a_handoff(old_capability, old_handoff)
    boundary._bind_n4a_handoff(new_capability, new_handoff)
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            new_capability, new_context, claimant="n4b_seal", handoff=old_handoff,
        )
    assert boundary._claim_n4a_lifecycle(
        new_capability, new_context, claimant="n4b_seal", handoff=new_handoff,
    ) is None
    assert old_context.generation_identity != new_context.generation_identity


def test_cross_context_handoff_refuses_without_consuming_registered_original():
    boundary = _boundary()
    context, _, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    other_context = replace(context, _registration_token=object())
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, other_context, claimant="n4b_seal", handoff=handoff,
        )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None


def test_handoff_from_other_n4a_invocation_refuses_without_consuming_origin():
    boundary = _boundary()
    context, primitive, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    other_primitive = replace(primitive, renderer_input_sha256="9" * 64)
    other_capability = N4ASealCapability(
        context.generation_identity, context._registration_token, object(), object(),
    )
    other_application = N4ATransientApplication(
        context.generation_identity, Path("/synthetic/other-invocation.app"),
        context._registration_token, object(), object(),
    )
    other_handoff = N4ASealHandoff(
        other_primitive, other_capability, handoff.projection, other_application,
    )
    boundary._register(other_application, context, context.generation_identity,
                       "transient-app", lifecycle_token=other_application._lifecycle_token)
    boundary._register(other_capability, context, context.generation_identity,
                       "seal-capability", primitive=other_primitive,
                       lifecycle_token=other_capability._lifecycle_token)
    boundary._bind_n4a_handoff(other_capability, other_handoff)
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="n4b_seal", handoff=other_handoff,
        )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None


def test_unrelated_value_equal_handoff_refuses_without_consuming_original():
    boundary = _boundary()
    context, _, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    unrelated = N4ASealHandoff(
        handoff.measured_primitive, handoff.capability,
        handoff.projection, handoff.source_application,
    )
    assert unrelated == handoff and unrelated is not handoff
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="n4b_seal", handoff=unrelated,
        )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None


def test_handoff_acceptance_is_registered_referent_identity():
    boundary = _boundary()
    context, _, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    with boundary._REGISTRY_LOCK:
        registered_ref = boundary._REGISTRY[id(capability)][6][0]
    assert registered_ref() is handoff
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None


def test_shared_lifecycle_helper_allows_exactly_one_direct_claim(monkeypatch):
    boundary = _boundary()
    context, primitive, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="legacy_consume",
    ) is primitive
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="n4b_seal", handoff=handoff,
        )

    context, _, capability, handoff = _direct_n4a_handoff(
        boundary, generation="e" * 64,
    )
    boundary._bind_n4a_handoff(capability, handoff)
    monkeypatch.setattr(
        boundary, "_take_compatibility_primitive",
        lambda record: (_ for _ in ()).throw(AssertionError("N4B read slot 5")),
    )
    assert boundary._claim_n4a_lifecycle(
        capability, context, claimant="n4b_seal", handoff=handoff,
    ) is None
    with boundary._REGISTRY_LOCK:
        claimed_record = boundary._REGISTRY[id(capability)]
    assert claimed_record[4] is True and claimed_record[5] is None
    with pytest.raises(EvidenceDagError):
        boundary._claim_n4a_lifecycle(
            capability, context, claimant="legacy_consume",
        )


def test_concurrent_direct_lifecycle_claims_allow_at_most_one():
    boundary = _boundary()
    context, primitive, capability, handoff = _direct_n4a_handoff(boundary)
    boundary._bind_n4a_handoff(capability, handoff)
    barrier = threading.Barrier(3)
    outcomes = []
    outcomes_lock = threading.Lock()

    def claim(claimant, candidate):
        barrier.wait()
        try:
            result = boundary._claim_n4a_lifecycle(
                capability, context, claimant=claimant, handoff=candidate,
            )
        except EvidenceDagError:
            outcome = (claimant, False, None)
        else:
            outcome = (claimant, True, result)
        with outcomes_lock:
            outcomes.append(outcome)

    threads = (
        threading.Thread(target=claim, args=("legacy_consume", None)),
        threading.Thread(target=claim, args=("n4b_seal", handoff)),
    )
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join(timeout=5)
        assert not thread.is_alive()
    successful = [outcome for outcome in outcomes if outcome[1]]
    assert len(successful) == 1
    if successful[0][0] == "legacy_consume":
        assert successful[0][2] is primitive
    else:
        assert successful[0][2] is None


def test_n4a_measurement_leaf_runs_once_and_same_object_enters_handoff(n4a_lineage, monkeypatch):
    boundary = _boundary()
    seen_s1, seen_s2 = [], []
    measurement_calls = []
    real_render = snapshot_mod.render_s2_from_s1
    def render(s1):
        seen_s1.append(s1)
        return real_render(s1)
    real_invoke = boundary.invoke_stage_b_build_app
    def invoke(s2, build_context):
        seen_s2.append(s2)
        return real_invoke(s2, build_context)
    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic-build",), 0, b"", b"")
    monkeypatch.setattr(snapshot_mod, "render_s2_from_s1", render)
    monkeypatch.setattr(boundary, "invoke_stage_b_build_app", invoke)
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    s8 = ModuleType("gate0.feasibility.macos_stage_b_evidence_s8")
    signed_bytes = b"synthetic codesign entitlement observation"
    def measure(application):
        measurement_calls.append(application)
        return subprocess.CompletedProcess(("synthetic-codesign",), 0, signed_bytes, b"")
    s8._run_codesign_entitlements = measure
    monkeypatch.setitem(sys.modules, "gate0.feasibility.macos_stage_b_evidence_s8", s8)
    result = boundary.measure_and_handoff_n4a(n4a_lineage["anchored_s1"], n4a_lineage["s2"],
                                               n4a_lineage["build_context"])
    assert len(seen_s1) == 1 and seen_s1[0] is n4a_lineage["anchored_s1"].frozen_s1
    assert seen_s2[0] is result.renderer_output_s2
    assert seen_s2[0] is not n4a_lineage["s2"]
    assert tuple(f.name for f in fields(result.primitive)) == (
        "format", "renderer_input_sha256", "renderer_input_octets",
        "signer_entitlements_sha256", "signer_entitlements_octets")
    assert result.primitive.signer_entitlements_sha256 == hashlib.sha256(signed_bytes).hexdigest()
    assert result.primitive.signer_entitlements_octets == len(signed_bytes)
    assert measurement_calls == [result.transient_application]
    assert result.n4b_handoff.measured_primitive is result.primitive
    assert result.n4b_handoff.capability is result.seal_capability
    assert result.n4b_handoff.source_application is result.transient_application
    assert result.n4b_handoff.projection.canonical_identity_json_bytes
    capability = result.seal_capability
    for forged in (copy.copy(capability), copy.deepcopy(capability),
                   replace(capability, _lifecycle_token=object())):
        with pytest.raises(EvidenceDagError):
            boundary._consume_n4a_primitive(forged, n4a_lineage["context"])
    other_context = replace(n4a_lineage["context"], generation_identity="e" * 64)
    with pytest.raises(EvidenceDagError):
        boundary._consume_n4a_primitive(capability, other_context)
    measured = boundary._consume_n4a_primitive(result.seal_capability, n4a_lineage["context"])
    assert measured is result.primitive
    with pytest.raises(EvidenceDagError, match="already consumed"):
        boundary._consume_n4a_primitive(result.seal_capability, n4a_lineage["context"])


def test_n4a_boundary_has_no_second_primitive_constructor_or_measurement_path():
    boundary = _boundary()
    tree = ast.parse(inspect.getsource(boundary))
    constructors = [node for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "N4ABoundaryPrimitive"]
    assert len(constructors) == 1
    assert constructors[0].lineno > 570


def test_n4a_boundary_returns_exact_primitive_capability_application_aliases():
    boundary = _boundary()
    result_type = get_type_hints(N4AProductionResult)
    assert result_type["n4b_handoff"] is N4ASealHandoff
    assert tuple(field.name for field in fields(N4AProductionResult))[-1] == "n4b_handoff"


def test_build_environment_starts_empty_and_has_exact_seven_values(n4a_lineage, monkeypatch):
    boundary = _boundary()
    expected = frozenset({
        "GATE0_STAGE_B_FROZEN_S2", "GATE0_STAGE_B_SEALED_DESTINATION", "STAGE_B_SIGN_IDENTITY", "HOME",
        "TMPDIR", "XDG_CACHE_HOME", "PATH",
    })
    assert boundary.BUILD_ENVIRONMENT_KEYS == expected
    observed = {}
    def fake_process(s2, build_context, private_s2_file, env):
        observed.update(env)
        build_context.sealed_destination.application_path.mkdir()
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    app = boundary.invoke_stage_b_build_app(n4a_lineage["s2"], n4a_lineage["build_context"])
    assert type(app) is N4ATransientApplication
    assert frozenset(observed) == expected
    assert "INJECTED_HOST_ENV" not in observed and "PYTHONPATH" not in observed
    assert observed["GATE0_STAGE_B_SEALED_DESTINATION"] == str(n4a_lineage["build_context"].sealed_destination.application_path)


def test_build_context_uses_verified_repository_context_only(n4a_lineage):
    boundary = _boundary()
    assert type(n4a_lineage["build_context"]) is VerifierOwnedBuildContext
    assert n4a_lineage["build_context"].repository_context is n4a_lineage["context"]
    assert tuple(__import__("inspect").signature(boundary._create_verifier_owned_build_context).parameters) == (
        "repository_context", "anchor",
    )


def test_private_s2_is_exclusive_nofollow_and_reread_exact(n4a_lineage):
    boundary = _boundary()
    path = boundary._write_private_s2(n4a_lineage["s2"], n4a_lineage["build_context"])
    assert path.read_bytes() == n4a_lineage["s2"].data
    with pytest.raises(EvidenceDagError):
        boundary._write_private_s2(n4a_lineage["s2"], n4a_lineage["build_context"])
    path.unlink()
    scratch = n4a_lineage["build_context"].sealed_destination.scratch_root
    saved_scratch = scratch.with_name("saved-scratch")
    outside = n4a_lineage["root"] / "outside"
    outside.mkdir()
    (outside / "private").mkdir()
    scratch.rename(saved_scratch)
    scratch.symlink_to(outside, target_is_directory=True)
    with pytest.raises(EvidenceDagError):
        boundary._write_private_s2(n4a_lineage["s2"], n4a_lineage["build_context"])
    assert not (outside / "private" / "S2.plist").exists()
    scratch.unlink()
    saved_scratch.rename(scratch)
    build_parent = scratch.parent
    saved_parent = build_parent.with_name("saved-build")
    build_parent.rename(saved_parent)
    build_parent.symlink_to(outside, target_is_directory=True)
    with pytest.raises(EvidenceDagError):
        boundary._write_private_s2(n4a_lineage["s2"], n4a_lineage["build_context"])
    assert not (outside / "private" / "S2.plist").exists()


def test_destination_absent_before_build_and_same_after_checkpoint(n4a_lineage, monkeypatch):
    boundary = _boundary()
    build_context = n4a_lineage["build_context"]
    destination = build_context.sealed_destination
    boundary._validate_destination_identity(destination, build_context.repository_context)
    calls = []
    def fake_process(s2, context, private_s2_file, env):
        calls.append((s2, context))
        write_capture_bundle(context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    s8 = ModuleType("gate0.feasibility.macos_stage_b_evidence_s8")
    s8._run_codesign_entitlements = lambda application: subprocess.CompletedProcess(
        ("synthetic-codesign",), 0, b"synthetic entitlements", b"")
    monkeypatch.setitem(sys.modules, "gate0.feasibility.macos_stage_b_evidence_s8", s8)
    result = boundary.measure_and_handoff_n4a(n4a_lineage["anchored_s1"], n4a_lineage["s2"], build_context)
    assert result.transient_application._subject_path == destination.application_path
    assert result.transient_application._subject_path.is_dir()
    assert not result.transient_application._subject_path.is_symlink()
    assert build_context.repository_context.canonical_root == n4a_lineage["root"]
    assert len(calls) == 1
    # Successful N4A consumes its verified repository context and anchored S1;
    # replay must fail before another renderer/build/sign observation.
    with pytest.raises(EvidenceDagError, match="already consumed"):
        boundary.measure_and_handoff_n4a(n4a_lineage["anchored_s1"], n4a_lineage["s2"], build_context)
    assert len(calls) == 1


def test_capture_producer_registration_lifecycle_order(capture_registered, monkeypatch):
    case = capture_registered
    boundary = case["boundary"]
    trace = case["trace"]
    assert case["binding"] is not None, "trusted registration-origin binding is absent"
    assert case["binding"].state == "ELIGIBLE", case["binding"].refusal_reason
    assert trace["reads"] == []
    producer_done = next(i for i, event in enumerate(trace["events"])
                         if event[0] == "producer-complete")
    registration = next(i for i, event in enumerate(trace["events"])
                        if event[0] == "metadata-registration")
    graph = next(i for i, event in enumerate(trace["events"])
                 if event[0] == "graph-open")
    assert producer_done < registration < graph
    assert len(trace["origin_fds"]) == 10
    assert len([e for e in trace["events"] if e[0] == "graph-open" and e[1] == "Contents"]) == 1
    before = len([e for e in trace["events"] if e[0] == "producer-start"])
    with pytest.raises(EvidenceDagError):
        boundary.invoke_stage_b_build_app(case["s2"], case["build_context"])
    after = len([e for e in trace["events"] if e[0] == "producer-start"])
    assert before == after == 1


def test_capture_registry_lock_has_no_filesystem_work(capture_registered):
    case = capture_registered
    lock_type = case["original_registry_lock_type"]
    assert lock_type is type(threading.Lock())
    assert case["binding"] is not None, "registry lock behavior requires capture graph establishment"
    assert len(case["binding"].session.entries) == 10
    probe = threading.Lock()
    assert probe.acquire(blocking=False)
    try:
        assert not probe.acquire(blocking=False)
    finally:
        probe.release()
    assert case["trace"]["registry_fs_violations"] == []


def test_capture_incomplete_registration_never_heals(n4a_lineage, monkeypatch):
    boundary = _boundary()
    def empty_bundle(s2, build_context, private_s2_file, env):
        build_context.sealed_destination.application_path.mkdir()
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", empty_bundle)
    application = boundary.invoke_stage_b_build_app(
        n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    binding = next((value for key, value in getattr(boundary, "_CAPTURE_BINDINGS", {}).items()
                    if getattr(value, "application", None) is application), None)
    assert binding is not None, "incomplete registration must retain terminal capture status"
    assert binding.state == "REFUSED"
    write_capture_bundle(application._subject_path)
    with pytest.raises(EvidenceDagError):
        boundary._begin_capture(application)


@pytest.mark.parametrize("failure", (
    "signer_invalid", "signer_raises", "post_signer_raises",
    "binding_establishment_raises", "graph_validation_raises",
))
def test_n4a_post_registration_failure_refuses_and_releases_capture(
        n4a_lineage, monkeypatch, failure):
    boundary = _boundary()
    projection = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_projection",
    )
    s8 = ModuleType("gate0.feasibility.macos_stage_b_evidence_s8")
    if failure == "signer_invalid":
        s8._run_codesign_entitlements = lambda application: object()
    elif failure == "signer_raises":
        def signer_raises(application):
            raise RuntimeError("synthetic signer observation failure")
        s8._run_codesign_entitlements = signer_raises
    else:
        s8._run_codesign_entitlements = lambda application: subprocess.CompletedProcess(
            ("synthetic",), 0, b"synthetic entitlements", b"",
        )
        if failure == "post_signer_raises":
            def primitive_raises(*args, **kwargs):
                raise ValueError("synthetic post-signer extraction failure")
            monkeypatch.setattr(boundary, "N4ABoundaryPrimitive", primitive_raises)
        elif failure == "binding_establishment_raises":
            original_record_check = boundary._registered_application_record
            record_checks = 0

            def fail_after_graph(application, context):
                nonlocal record_checks
                record_checks += 1
                if record_checks == 2:
                    raise RuntimeError("synthetic binding establishment failure")
                return original_record_check(application, context)

            monkeypatch.setattr(boundary, "_registered_application_record", fail_after_graph)
        else:
            def graph_validation_raises(session):
                raise RuntimeError("synthetic graph validation failure")
            monkeypatch.setattr(projection, "_validate_origin_graph", graph_validation_raises)
    monkeypatch.setitem(sys.modules, "gate0.feasibility.macos_stage_b_evidence_s8", s8)

    registry_records = {}
    cleanup_under_locks = []
    original_close = projection.os.close

    def observe_cleanup_close(fd):
        if boundary._REGISTRY_LOCK.locked() or boundary._SOURCE_LIFECYCLE_LOCK.locked():
            cleanup_under_locks.append(fd)
        return original_close(fd)
    monkeypatch.setattr(projection.os, "close", observe_cleanup_close)

    def fake_process(s2, build_context, private_s2_file, env):
        registry_records["context"] = boundary._REGISTRY[id(n4a_lineage["context"])]
        registry_records["anchored_s1"] = boundary._REGISTRY[id(n4a_lineage["anchored_s1"])]
        app_path = build_context.sealed_destination.application_path
        write_capture_bundle(app_path)
        app_files_before.update({path: path.read_bytes() for path in app_path.rglob("*")
                                 if path.is_file()})
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    published = []
    monkeypatch.setattr(boundary, "_publish_capture", lambda *args, **kwargs: published.append(args))

    app_files_before = {}
    expected_error = {
        "signer_invalid": EvidenceDagError,
        "signer_raises": RuntimeError,
        "post_signer_raises": ValueError,
        "binding_establishment_raises": RuntimeError,
        "graph_validation_raises": RuntimeError,
    }[failure]
    with pytest.raises(expected_error):
        boundary.measure_and_handoff_n4a(
            n4a_lineage["anchored_s1"], n4a_lineage["s2"], n4a_lineage["build_context"],
        )

    binding = next(value for value in boundary._CAPTURE_BINDINGS.values()
                   if value.application._subject_path
                   == n4a_lineage["build_context"].sealed_destination.application_path)
    application = binding.application
    assert binding.state == "REFUSED"
    assert binding.session is not None and binding.session.released
    assert binding.session.entries == []
    assert cleanup_under_locks == []
    assert published == []
    assert app_files_before
    assert {path: path.read_bytes() for path in app_files_before} == app_files_before
    assert application._subject_path.is_dir()
    assert not application._subject_path.is_symlink()
    assert boundary._registered_application_record(application, n4a_lineage["context"])
    assert application._subject_path == n4a_lineage["build_context"].sealed_destination.application_path
    context_record = registry_records["context"]
    anchored_record = registry_records["anchored_s1"]
    assert boundary._REGISTRY[id(n4a_lineage["context"])] == context_record
    assert boundary._REGISTRY[id(n4a_lineage["anchored_s1"])] == anchored_record
    assert context_record[4] is False and anchored_record[4] is False
    with pytest.raises(EvidenceDagError):
        projection.capture_signed_image_projection_source(application)


def test_capture_invalidation_during_acquiring_never_publishes_eligibility(
        n4a_lineage, monkeypatch):
    boundary = _boundary()
    projection = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_projection",
    )
    reserved = threading.Event()
    resume = threading.Event()
    original_acquire = projection._acquire_origin_graph
    original_open = os.open
    fs_under_locks = []
    acquired_sessions = []

    def paused_acquire(context, application):
        reserved.set()
        assert resume.wait(5), "test did not resume descriptor acquisition"
        session = original_acquire(context, application)
        acquired_sessions.append(session)
        return session

    def checked_open(path, flags, *args, **kwargs):
        if boundary._REGISTRY_LOCK.locked() or boundary._SOURCE_LIFECYCLE_LOCK.locked():
            fs_under_locks.append((path, kwargs.get("dir_fd")))
        return original_open(path, flags, *args, **kwargs)

    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    monkeypatch.setattr(projection, "_acquire_origin_graph", paused_acquire)
    monkeypatch.setattr(os, "open", checked_open)
    monkeypatch.setattr(os, "supports_dir_fd", set(os.supports_dir_fd) | {checked_open})
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    outcome = {}

    def build():
        try:
            outcome["application"] = boundary.invoke_stage_b_build_app(
                n4a_lineage["s2"], n4a_lineage["build_context"],
            )
        except BaseException as exc:
            outcome["error"] = exc

    worker = threading.Thread(target=build)
    worker.start()
    assert reserved.wait(5), "capture binding was not reserved before graph acquisition"
    binding = next(value for value in boundary._CAPTURE_BINDINGS.values()
                   if value.context is n4a_lineage["context"]
                   and value.state == "ACQUIRING")
    boundary._request_capture_invalidation(binding.application, "synthetic lifecycle invalidation")
    resume.set()
    worker.join(5)
    assert not worker.is_alive()
    assert "error" not in outcome
    assert outcome.get("application") is binding.application
    assert binding.state == "REFUSED"
    assert len(acquired_sessions) == 1
    assert acquired_sessions[0].released
    assert acquired_sessions[0].entries == []
    assert not fs_under_locks, f"filesystem work ran under a lifecycle/registry lock: {fs_under_locks}"
    with pytest.raises(EvidenceDagError):
        boundary._begin_capture(binding.application)


@pytest.mark.parametrize("case", [
    "repository_context-shallow_copy", "repository_context-deep_copy",
    "repository_context-manual_reconstruction", "repository_context-copied_guard",
    "repository_context-changed_path", "repository_context-changed_generation",
    "repository_context-stale_lifecycle", "repository_context-replay_after_consumption",
    "anchored_s1-shallow_copy", "anchored_s1-deep_copy", "anchored_s1-manual_reconstruction",
    "anchored_s1-copied_guard", "anchored_s1-changed_path", "anchored_s1-changed_generation",
    "anchored_s1-stale_lifecycle", "anchored_s1-replay_after_consumption",
    "sealed_destination-shallow_copy", "sealed_destination-deep_copy",
    "sealed_destination-manual_reconstruction", "sealed_destination-copied_guard",
    "sealed_destination-changed_path", "sealed_destination-changed_generation",
    "sealed_destination-stale_lifecycle", "sealed_destination-replay_after_consumption",
    "signing_identity-shallow_copy", "signing_identity-deep_copy",
    "signing_identity-manual_reconstruction", "signing_identity-copied_guard",
    "signing_identity-changed_path", "signing_identity-changed_generation",
    "signing_identity-stale_lifecycle", "signing_identity-replay_after_consumption",
    "build_context-shallow_copy", "build_context-deep_copy",
    "build_context-manual_reconstruction", "build_context-copied_guard",
    "build_context-changed_path", "build_context-changed_generation",
    "build_context-stale_lifecycle", "build_context-replay_after_consumption",
    "seal_capability-shallow_copy", "seal_capability-deep_copy",
    "seal_capability-manual_reconstruction", "seal_capability-copied_guard",
    "seal_capability-changed_path", "seal_capability-changed_generation",
    "seal_capability-stale_lifecycle", "seal_capability-replay_after_consumption",
    "transient_application-shallow_copy", "transient_application-deep_copy",
    "transient_application-manual_reconstruction", "transient_application-copied_guard",
    "transient_application-changed_path", "transient_application-changed_generation",
    "transient_application-stale_lifecycle", "transient_application-replay_after_consumption",
], ids=lambda case: case)
def test_registered_handle_forgery_fails_before_leaf(case):
    boundary = _boundary()
    kind, mutation = case.split("-", 1)
    ctx = VerifiedRepositoryContext(Path("/synthetic/repo"), Path("/synthetic/repo/.git"),
        "a"*40, "b"*40, "c"*64, 1, 2, object())
    s1 = FrozenArtifact("S1", "S1.json", b"{}", "0"*64, 2)
    classes = {
        "repository_context": lambda: ctx,
        "anchored_s1": lambda: AnchoredS1Handle("a"*40, "S1.json", "d"*40, s1, "c"*64, ctx._registration_token, object()),
        "sealed_destination": lambda: VerifierOwnedSealedDestination(Path("/synthetic/root"), Path("/synthetic/root/app"), "c"*64, ctx._registration_token, object()),
        "signing_identity": lambda: VerifierOwnedSigningIdentity("opaque", "c"*64, ctx._registration_token, object()),
        "build_context": lambda: VerifierOwnedBuildContext(ctx,
            VerifierOwnedSealedDestination(Path("/synthetic/root"), Path("/synthetic/root/app"), "c"*64, ctx._registration_token, object()),
            VerifierOwnedSigningIdentity("opaque", "c"*64, ctx._registration_token, object()), "c"*64, object()),
        "seal_capability": lambda: N4ASealCapability("c"*64, ctx._registration_token, object(), object()),
        "transient_application": lambda: N4ATransientApplication("c"*64, Path("/synthetic/root/app"), ctx._registration_token, object(), object()),
    }
    candidate = classes[kind]()
    if mutation in {"shallow_copy", "copied_guard"}:
        candidate = copy.copy(candidate)
    elif mutation == "deep_copy":
        candidate = copy.deepcopy(candidate)
    elif mutation == "manual_reconstruction":
        candidate = type(candidate)(*(getattr(candidate, f.name) for f in fields(candidate)))
    elif mutation == "changed_generation" and hasattr(candidate, "generation_identity"):
        candidate = replace(candidate, generation_identity="e"*64)
    elif mutation == "changed_path":
        if hasattr(candidate, "application_path"):
            candidate = replace(candidate, application_path=Path("/attacker/app"))
        elif hasattr(candidate, "_subject_path"):
            candidate = replace(candidate, _subject_path=Path("/attacker/app"))
        elif hasattr(candidate, "canonical_root"):
            candidate = replace(candidate, canonical_root=Path("/attacker/repo"))
        elif hasattr(candidate, "s1_repository_path"):
            candidate = replace(candidate, s1_repository_path="attacker/S1.json")
        else:
            candidate = replace(candidate, _registration_token=object()) if hasattr(candidate, "_registration_token") else candidate
    elif mutation == "stale_lifecycle" and hasattr(candidate, "_lifecycle_token"):
        candidate = replace(candidate, _lifecycle_token=object())
    try:
        if kind == "repository_context":
            git_mod._validate_verified_repository_context(candidate)
        elif kind == "anchored_s1":
            anchor_mod._extract_registered_anchored_s1(candidate, ctx)
        else:
            boundary._validate_registered_handle(candidate, ctx)
    except Exception:
        return
    raise AssertionError(f"forged or replayed {case} was accepted")


@pytest.mark.parametrize("oracle_request", ORACLE_INSPECTION_REQUESTS, ids=lambda x: x.surface_id)
def test_oracle_request_is_observed_then_compared(oracle_request):
    assert "expected" not in oracle_request.__dataclass_fields__
    observation = inspect_oracle_request(oracle_request)
    assert compare_oracle_observation(observation, oracle_expectation_for(oracle_request.surface_id))


@pytest.mark.parametrize(
    "mechanism",
    sorted({x.mechanism for x in ORACLE_INSPECTION_REQUESTS}, key=lambda x: x.value),
    ids=lambda x: x.value,
)
def test_oracle_mechanism_positive_falsifier(mechanism):
    request, tree = positive_falsifier_for(mechanism)
    observation = inspect_oracle_request_against_tree(request, tree)
    assert observation_has_forbidden_match(observation)


def test_oracle_inspector_cannot_echo_expectation():
    assert oracle_echo_inspector_falsifier() is False


@pytest.mark.parametrize("phase", ("during_read", "before_publish"))
def test_capture_lifecycle_loss_and_cleanup_attempt_refuse(capture_registered, monkeypatch, phase):
    case = capture_registered
    boundary = case["boundary"]
    projection = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_projection",
    )
    binding = case["binding"]
    assert binding is not None
    physical_fds = set(binding.session.role_fds.values())
    if phase == "during_read":
        original_read = projection.os.read
        invalidated = False
        def invalidate_after_read(fd, size):
            nonlocal invalidated
            data = original_read(fd, size)
            if fd in physical_fds and not invalidated:
                invalidated = True
                boundary._request_capture_invalidation(case["application"], "synthetic lifecycle loss")
                boundary._request_capture_invalidation(case["application"], "idempotent repeated loss")
                assert not case["trace"]["closed_origin_fds"]
            return data
        monkeypatch.setattr(projection.os, "read", invalidate_after_read)
    else:
        original_publish = boundary._publish_capture
        reached = threading.Event()
        resume = threading.Event()
        outcome = []
        def pause_before_publish(*args, **kwargs):
            reached.set()
            assert resume.wait(3), "test publication barrier timed out"
            return original_publish(*args, **kwargs)
        monkeypatch.setattr(boundary, "_publish_capture", pause_before_publish)
        def run_capture():
            try:
                outcome.append(projection.capture_signed_image_projection_source(case["application"]))
            except BaseException as exc:
                outcome.append(exc)
        worker = threading.Thread(target=run_capture)
        worker.start()
        assert reached.wait(3), "capture did not reach pre-publication barrier"
        assert boundary._REGISTRY_LOCK.acquire(blocking=False)
        boundary._REGISTRY_LOCK.release()
        boundary._request_capture_invalidation(case["application"], "pre-publication cleanup attempt")
        boundary._request_capture_invalidation(case["application"], "repeated cleanup attempt")
        assert not case["trace"]["closed_origin_fds"]
        resume.set()
        worker.join(3)
        assert not worker.is_alive()
        assert len(outcome) == 1 and isinstance(outcome[0], EvidenceDagError)
    if phase == "during_read":
        with pytest.raises(EvidenceDagError):
            projection.capture_signed_image_projection_source(case["application"])
        assert invalidated
    assert binding.state == "REFUSED"
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])
    record = boundary._REGISTRY[id(case["application"])]
    assert record[0] is case["application"] and record[3] == "transient-app"
    boundary._validate_registered_handle(case["application"], case["context"])


def test_seal_n4b_builds_exact_additive_tree(n4a_lineage, monkeypatch):
    boundary = _boundary()
    from gate0.feasibility import macos_stage_b_evidence_seal as seal_mod
    seen = []
    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic-build",), 0, b"", b"")
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    s8 = ModuleType("gate0.feasibility.macos_stage_b_evidence_s8")
    s8._run_codesign_entitlements = lambda app: (seen.append(app), subprocess.CompletedProcess(("synthetic-codesign",), 0, b"synthetic signed bytes", b""))[1]
    monkeypatch.setitem(sys.modules, "gate0.feasibility.macos_stage_b_evidence_s8", s8)
    result = boundary.measure_and_handoff_n4a(n4a_lineage["anchored_s1"], n4a_lineage["s2"], n4a_lineage["build_context"])
    sealed = seal_mod.seal_n4b(n4a_lineage["anchor"], result.n4b_handoff)
    assert sealed.parent_s7_commit_sha == n4a_lineage["anchor"].commit_sha
    assert len(sealed.projection_members) == 8
    assert sealed.projection_members == tuple(f"S9/{name}" for name in (
        "executable-code-region.bin", "Info.plist", "CodeResources", "superblob-index.bin",
        "CodeDirectory", "Entitlements.blob", "DER-Entitlements.blob", "identity.json"))
    assert seen == [result.transient_application]
    from gate0.feasibility import macos_stage_b_evidence_git as seal_git
    assert seal_git.commit_parent(sealed.commit_sha) == n4a_lineage["anchor"].commit_sha
    expected = (
        result.n4b_handoff.projection.executable_code_region_bytes,
        result.n4b_handoff.projection.info_plist_bytes,
        result.n4b_handoff.projection.code_resources_bytes,
        result.n4b_handoff.projection.superblob_index_bytes,
        result.n4b_handoff.projection.code_directory_bytes,
        result.n4b_handoff.projection.entitlements_blob_bytes,
        result.n4b_handoff.projection.der_entitlements_blob_bytes,
        result.n4b_handoff.projection.canonical_identity_json_bytes,
    )
    for path, data in zip(sealed.projection_members, expected):
        assert seal_git.read_blob_at(sealed.commit_sha, path) == data


def _produce_registered_n4a_handoff(n4a_lineage, monkeypatch):
    boundary = _boundary()
    from gate0.feasibility import macos_stage_b_evidence_seal as seal_mod

    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic-build",), 0, b"", b"")

    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    s8 = ModuleType("gate0.feasibility.macos_stage_b_evidence_s8")
    s8._run_codesign_entitlements = lambda app: subprocess.CompletedProcess(
        ("synthetic-codesign",), 0, b"synthetic signed bytes", b"",
    )
    monkeypatch.setitem(sys.modules, "gate0.feasibility.macos_stage_b_evidence_s8", s8)
    result = boundary.measure_and_handoff_n4a(
        n4a_lineage["anchored_s1"], n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    return boundary, seal_mod, result


def test_slot_poisoning_does_not_change_n4b_primitive_bytes(n4a_lineage, monkeypatch):
    boundary, seal_mod, result = _produce_registered_n4a_handoff(n4a_lineage, monkeypatch)

    def poisoned(_record):
        raise AssertionError("N4B consulted the legacy compatibility primitive slot")

    monkeypatch.setattr(boundary, "_take_compatibility_primitive", poisoned)
    sealed = seal_mod.seal_n4b(n4a_lineage["anchor"], result.n4b_handoff)
    from gate0.feasibility import macos_stage_b_evidence_git as seal_git
    identity_bytes = seal_git.read_blob_at(sealed.commit_sha, "S9/identity.json")
    assert identity_bytes == result.n4b_handoff.projection.canonical_identity_json_bytes
    identity = json.loads(identity_bytes)
    primitive = result.n4b_handoff.measured_primitive
    assert identity["n4a_boundary_primitive"] == {
        "format": primitive.format,
        "renderer_input_sha256": primitive.renderer_input_sha256,
        "renderer_input_octets": primitive.renderer_input_octets,
        "signer_entitlements_sha256": primitive.signer_entitlements_sha256,
        "signer_entitlements_octets": primitive.signer_entitlements_octets,
    }


def test_cross_context_application_projection_pair_refuses(n4a_lineage, monkeypatch):
    _, seal_mod, result = _produce_registered_n4a_handoff(n4a_lineage, monkeypatch)
    foreign_application = replace(
        result.transient_application, _repository_context_token=object(),
    )
    foreign_pair = replace(result.n4b_handoff, source_application=foreign_application)
    with pytest.raises(EvidenceDagError):
        seal_mod.seal_n4b(n4a_lineage["anchor"], foreign_pair)
    sealed = seal_mod.seal_n4b(n4a_lineage["anchor"], result.n4b_handoff)
    assert sealed.parent_s7_commit_sha == n4a_lineage["anchor"].commit_sha


@pytest.mark.parametrize("first_consumer", ("legacy", "seal"))
def test_legacy_then_seal_and_seal_then_legacy_each_allow_one(
    n4a_lineage, monkeypatch, first_consumer,
):
    boundary, seal_mod, result = _produce_registered_n4a_handoff(n4a_lineage, monkeypatch)
    if first_consumer == "legacy":
        assert boundary._consume_n4a_primitive(
            result.seal_capability, n4a_lineage["context"],
        ) is result.primitive
        git_calls = []
        original_git_input = seal_mod._git_input
        def record_git_input(argv, input_bytes=None):
            git_calls.append(argv)
            return original_git_input(argv, input_bytes)
        monkeypatch.setattr(seal_mod, "_git_input", record_git_input)
        with pytest.raises(EvidenceDagError):
            seal_mod.seal_n4b(n4a_lineage["anchor"], result.n4b_handoff)
        assert git_calls == []
    else:
        seal_mod.seal_n4b(n4a_lineage["anchor"], result.n4b_handoff)
        with pytest.raises(EvidenceDagError):
            boundary._consume_n4a_primitive(
                result.seal_capability, n4a_lineage["context"],
            )


def test_concurrent_claim_race_allows_at_most_one_public_consumer(n4a_lineage, monkeypatch):
    boundary, seal_mod, result = _produce_registered_n4a_handoff(n4a_lineage, monkeypatch)
    barrier = threading.Barrier(3)
    outcomes = []
    outcome_lock = threading.Lock()

    def consume(kind):
        barrier.wait()
        try:
            value = (seal_mod.seal_n4b(n4a_lineage["anchor"], result.n4b_handoff)
                     if kind == "seal" else boundary._consume_n4a_primitive(
                         result.seal_capability, n4a_lineage["context"],
                     ))
        except EvidenceDagError:
            outcome = (kind, "expected_refusal", None)
        except BaseException as exc:
            outcome = (kind, "unexpected_exception", repr(exc))
        else:
            outcome = (kind, "success", value)
        with outcome_lock:
            outcomes.append(outcome)

    workers = [threading.Thread(target=consume, args=(kind,)) for kind in ("legacy", "seal")]
    for worker in workers:
        worker.start()
    barrier.wait()
    for worker in workers:
        worker.join(timeout=15)
        assert not worker.is_alive()
    assert len(outcomes) == 2
    assert all(row[1] != "unexpected_exception" for row in outcomes), outcomes
    winners = [row for row in outcomes if row[1] == "success"]
    assert len(winners) == 1
    assert sum(row[1] == "expected_refusal" for row in outcomes) == 1
    if winners[0][0] == "legacy":
        assert winners[0][2] is result.primitive
    else:
        assert winners[0][2].parent_s7_commit_sha == n4a_lineage["anchor"].commit_sha
