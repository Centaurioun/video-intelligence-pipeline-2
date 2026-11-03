"""Task-3 registration-origin capture tests over synthetic temporary bundles."""
from __future__ import annotations

import importlib
import importlib.util
import os
from pathlib import Path
import subprocess
import copy
from dataclasses import fields, replace
import hashlib
import inspect
import json
import re
import shutil
import stat
import struct
import threading

import pytest

from gate0.feasibility.macos_stage_b_evidence_constants import EvidenceDagError
from tests.gate0.unit.evidence_dag_fixtures import (
    CANONICAL_IDENTITY_JSON_FIXTURE,
    capture_bundle_bytes,
    write_capture_bundle,
)
from tests.gate0.unit.test_evidence_boundary import capture_registered, n4a_lineage


def _projection_module():
    spec = importlib.util.find_spec(
        "gate0.feasibility.macos_stage_b_evidence_projection",
    )
    assert spec is not None, "Task-3 retained-descriptor projection module is absent"
    return importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_projection",
    )


def _replace_with_symlink(path: Path):
    saved = path.with_name(path.name + ".task3-saved")
    path.rename(saved)
    saved_target = saved.resolve()
    path.symlink_to(saved_target, target_is_directory=saved.is_dir())

    def restore():
        path.unlink()
        saved.rename(path)

    return restore


def _capture_edge_paths(case):
    root = case["root"]
    app = case["application"]._subject_path
    return {
        "root": root,
        "build": root / ".stage-b-build",
        "generation": root / ".stage-b-build" / case["context"].generation_identity,
        "application": app,
        "Contents": app / "Contents",
        "MacOS": app / "Contents/MacOS",
        "_CodeSignature": app / "Contents/_CodeSignature",
        "executable": app / "Contents/MacOS/StageBSandboxRunner",
        "info_plist": app / "Contents/Info.plist",
        "code_resources": app / "Contents/_CodeSignature/CodeResources",
    }


def _replace_capture_edge_with_identical_copy(case, edge):
    path = _capture_edge_paths(case)[edge]
    saved = path.with_name(path.name + ".task3-origin")
    path.rename(saved)
    if saved.is_dir():
        shutil.copytree(saved, path, copy_function=shutil.copy2)
    else:
        shutil.copy2(saved, path)
    return saved


def _detach_capture_edge(case, edge):
    path = _capture_edge_paths(case)[edge]
    saved = path.with_name(path.name + ".task3-detached")
    path.rename(saved)
    return saved


def _path_content_manifest(path: Path):
    """Describe a synthetic file/tree by entry type and exact file bytes."""
    if path.is_file():
        return ((".", "file", path.read_bytes()),)
    entries = [(".", "directory", b"")]
    for item in sorted(path.rglob("*")):
        relative = item.relative_to(path).as_posix()
        if item.is_symlink():
            entries.append((relative, "symlink", os.fsencode(os.readlink(item))))
        elif item.is_dir():
            entries.append((relative, "directory", b""))
        else:
            entries.append((relative, "file", item.read_bytes()))
    return tuple(entries)


def _synthetic_tree_manifest(root: Path):
    """Capture all synthetic repo paths to prove capture adds no durable output."""
    entries = []
    for item in sorted(root.rglob("*")):
        relative = item.relative_to(root).as_posix()
        if item.is_symlink():
            entries.append((relative, "symlink", os.fsencode(os.readlink(item))))
        elif item.is_dir():
            entries.append((relative, "directory", b""))
        else:
            entries.append((relative, "file", item.read_bytes()))
    return tuple(entries)


def _malformed_capture_executable(executable: bytes, case: str) -> bytes:
    """Mutate only the deterministic signed-image fixture before registration."""
    value = bytearray(executable)
    signature_offset = 512
    if case == "duplicate_lc_code_signature":
        command = bytes(value[32:48])
        struct.pack_into("<I", value, 16, 2)
        struct.pack_into("<I", value, 20, 32)
        value[48:64] = command
        cd_offset = struct.unpack_from(">I", value, signature_offset + 16)[0]
        cd_start = signature_offset + cd_offset
        hash_offset = struct.unpack_from(">I", value, cd_start + 16)[0]
        hash_size = value[cd_start + 36]
        struct.pack_into(
            f">{hash_size}s", value, cd_start + hash_offset,
            hashlib.sha256(value[:512]).digest(),
        )
    elif case == "signature_dataoff_before_commands":
        struct.pack_into("<I", value, 40, 47)
    elif case == "signature_datasize_out_of_bounds":
        struct.pack_into("<I", value, 44, len(value) - signature_offset + 1)
    elif case == "superblob_offset_alias":
        cd_offset = struct.unpack_from(">I", value, signature_offset + 16)[0]
        struct.pack_into(">I", value, signature_offset + 12 + 8 + 4, cd_offset)
    elif case == "superblob_partial_overlap":
        struct.pack_into(">I", value, signature_offset + 12 + 8 + 4, 60)
        struct.pack_into(">II", value, signature_offset + 60, 0xFADE0C01, 24)
    elif case == "truncated_code_directory_hash_extent":
        cd_offset = struct.unpack_from(">I", value, signature_offset + 16)[0]
        struct.pack_into(">I", value, signature_offset + cd_offset + 16, 279)
    elif case == "unsupported_code_directory_version_next":
        cd_offset = struct.unpack_from(">I", value, signature_offset + 16)[0]
        struct.pack_into(">I", value, signature_offset + cd_offset + 8, 0x20002)
    elif case == "unsupported_code_directory_version_future":
        cd_offset = struct.unpack_from(">I", value, signature_offset + 16)[0]
        struct.pack_into(">I", value, signature_offset + cd_offset + 8, 0xFFFFFFFF)
    else:
        raise AssertionError(f"unknown malformed synthetic case: {case}")
    return bytes(value)


def _register_malformed_capture(n4a_lineage, monkeypatch, malformed_case: str):
    """Register a real descriptor graph whose synthetic executable is malformed."""
    boundary = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_boundary",
    )
    projection = _projection_module()
    root = n4a_lineage["root"]
    opened = []
    closed = []
    real_open = os.open
    real_close = os.close

    def traced_open(path, flags, *args, **kwargs):
        fd = real_open(path, flags, *args, **kwargs)
        if kwargs.get("dir_fd") is not None or Path(path) == root:
            opened.append(fd)
        return fd

    def traced_close(fd):
        real_close(fd)
        if fd in opened:
            closed.append(fd)

    monkeypatch.setattr(projection.os, "open", traced_open)
    monkeypatch.setattr(projection.os, "close", traced_close)
    monkeypatch.setattr(
        projection.os, "supports_dir_fd",
        set(projection.os.supports_dir_fd) | {traced_open},
    )

    def synthetic_process(_s2, build_context, _private_s2_file, _env):
        application_path = build_context.sealed_destination.application_path
        executable, info, resources, _expected = capture_bundle_bytes()
        executable_path = application_path / "Contents/MacOS/StageBSandboxRunner"
        (application_path / "Contents/MacOS").mkdir(parents=True)
        (application_path / "Contents/_CodeSignature").mkdir()
        executable_path.write_bytes(
            _malformed_capture_executable(executable, malformed_case),
        )
        (application_path / "Contents/Info.plist").write_bytes(info)
        (application_path / "Contents/_CodeSignature/CodeResources").write_bytes(resources)
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    monkeypatch.setattr(boundary, "_run_stage_b_build_process", synthetic_process)
    application = boundary.invoke_stage_b_build_app(
        n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    binding = boundary._CAPTURE_BINDINGS[id(application)]
    assert binding.application is application
    return {
        "boundary": boundary,
        "projection": projection,
        "application": application,
        "binding": binding,
        "opened": opened,
        "closed": closed,
        "root": root,
    }


def _invoke_with_registration_mutation(n4a_lineage, monkeypatch, edge):
    boundary = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_boundary",
    )
    original_register = boundary._register
    root = n4a_lineage["root"]
    application_path = n4a_lineage["build_context"].sealed_destination.application_path
    targets = {
        "root": root,
        "build": root / ".stage-b-build",
        "generation": root / ".stage-b-build" / n4a_lineage["build_context"].generation_identity,
        "application": application_path,
        "Contents": application_path / "Contents",
        "MacOS": application_path / "Contents/MacOS",
        "_CodeSignature": application_path / "Contents/_CodeSignature",
        "executable": application_path / "Contents/MacOS/StageBSandboxRunner",
        "info_plist": application_path / "Contents/Info.plist",
        "code_resources": application_path / "Contents/_CodeSignature/CodeResources",
    }
    restored = []

    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    def register(handle, context, generation, kind, *args, **kwargs):
        original_register(handle, context, generation, kind, *args, **kwargs)
        if kind == "transient-app":
            assert targets[edge].exists(), f"registration-mutation target is absent: {targets[edge]}"
            restored.append(_replace_with_symlink(targets[edge]))

    monkeypatch.setattr(boundary, "_register", register)
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    try:
        application = boundary.invoke_stage_b_build_app(
            n4a_lineage["s2"], n4a_lineage["build_context"],
        )
        binding = next((value for value in getattr(boundary, "_CAPTURE_BINDINGS", {}).values()
                        if getattr(value, "application", None) is application), None)
        return boundary, application, binding, restored
    except BaseException:
        for restore in reversed(restored):
            restore()
        raise


def test_capture_registration_graph_precedes_bytes(capture_registered):
    projection = _projection_module()
    case = capture_registered
    binding = case["binding"]
    assert binding is not None, "trusted registration-origin binding is absent"
    assert binding.state == "ELIGIBLE"
    assert len(binding.session.entries) == 10
    assert case["trace"]["reads"] == []
    assert len([e for e in case["trace"]["events"] if e[0] == "graph-open" and e[1] == "Contents"]) == 1
    assert len(case["trace"]["origin_fds"]) == 10
    assert not case["trace"]["closed_origin_fds"]
    assert all(os.fstat(fd).st_mode for fd in binding.session.descriptors)
    assert projection._validate_origin_graph(binding.session) is None


@pytest.mark.parametrize(
    "edge",
    ("root", "build", "generation", "application", "Contents", "MacOS",
     "_CodeSignature", "executable", "info_plist", "code_resources"),
)
def test_capture_fixed_graph_nofollow_refuses_registration(edge, n4a_lineage, monkeypatch):
    _projection_module()
    boundary, application, binding, restored = _invoke_with_registration_mutation(
        n4a_lineage, monkeypatch, edge,
    )
    try:
        assert binding is not None, "registration must retain terminal capture status"
        assert binding.state == "REFUSED", binding.refusal_reason
        with pytest.raises(EvidenceDagError):
            boundary._begin_capture(application)
    finally:
        for restore in reversed(restored):
            restore()


@pytest.mark.parametrize(
    "missing_semantics",
    ("O_NOFOLLOW", "O_DIRECTORY", "O_CLOEXEC", "open_dir_fd",
     "stat_follow_symlinks", "NotImplementedError", "close_error_after_real_close"),
)
def test_capture_required_platform_semantics_fail_closed(missing_semantics, n4a_lineage, monkeypatch):
    _projection_module()
    boundary = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_boundary",
    )
    projection = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_projection",
    )
    if missing_semantics in {"O_NOFOLLOW", "O_DIRECTORY", "O_CLOEXEC"}:
        monkeypatch.delattr(projection.os, missing_semantics, raising=False)
    elif missing_semantics == "open_dir_fd":
        monkeypatch.setattr(
            projection.os, "supports_dir_fd",
            set(projection.os.supports_dir_fd) - {projection.os.open},
        )
    elif missing_semantics == "stat_follow_symlinks":
        monkeypatch.setattr(
            projection.os, "supports_follow_symlinks",
            set(projection.os.supports_follow_symlinks) - {projection.os.stat},
        )
    elif missing_semantics == "NotImplementedError":
        real_open = projection.os.open
        def unavailable_open(path, flags, *args, **kwargs):
            if "dir_fd" in kwargs:
                raise NotImplementedError("synthetic missing dir_fd behavior")
            return real_open(path, flags, *args, **kwargs)
        monkeypatch.setattr(projection.os, "open", unavailable_open)
    else:
        real_open = projection.os.open
        real_close = projection.os.close
        directory_opens = 0
        acquired_fds = []
        close_raised = False
        failed_sessions = []
        real_release = projection._release_origin_graph

        def fail_during_graph(path, flags, *args, **kwargs):
            nonlocal directory_opens
            if "dir_fd" in kwargs:
                directory_opens += 1
                if directory_opens == 2:
                    raise NotImplementedError("synthetic graph acquisition interruption")
            fd = real_open(path, flags, *args, **kwargs)
            if path == n4a_lineage["root"] or "dir_fd" in kwargs:
                acquired_fds.append(fd)
            return fd

        def close_then_report_error(fd):
            nonlocal close_raised
            real_close(fd)
            if not close_raised:
                close_raised = True
                raise OSError("synthetic close report after real close")

        def observe_release(session):
            failed_sessions.append(session)
            return real_release(session)

        monkeypatch.setattr(projection.os, "open", fail_during_graph)
        monkeypatch.setattr(
            projection.os, "supports_dir_fd",
            set(projection.os.supports_dir_fd) | {fail_during_graph},
        )
        monkeypatch.setattr(projection.os, "close", close_then_report_error)
        monkeypatch.setattr(projection, "_release_origin_graph", observe_release)

    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    application = boundary.invoke_stage_b_build_app(
        n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    binding = next((value for value in getattr(boundary, "_CAPTURE_BINDINGS", {}).values()
                    if getattr(value, "application", None) is application), None)
    assert binding is not None, "unsupported graph semantics must remain a terminal refusal"
    assert binding.state == "REFUSED"
    if missing_semantics == "close_error_after_real_close":
        assert failed_sessions, "partial graph session was not retained for cleanup disposition"
        assert failed_sessions[0].entries, "cleanup failure discarded uncertain descriptor ownership"
        for fd in acquired_fds:
            with pytest.raises(OSError):
                os.fstat(fd)
    with pytest.raises(EvidenceDagError):
        boundary._begin_capture(application)


def test_capture_graph_acquisition_uses_parent_fd_and_nofollow_flags(
        n4a_lineage, monkeypatch):
    projection = _projection_module()
    boundary = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_boundary",
    )
    real_open = os.open
    calls = []

    def observed_open(path, flags, *args, **kwargs):
        calls.append((path, flags, kwargs.get("dir_fd")))
        return real_open(path, flags, *args, **kwargs)

    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    monkeypatch.setattr(os, "open", observed_open)
    monkeypatch.setattr(os, "supports_dir_fd", set(os.supports_dir_fd) | {observed_open})
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    application = boundary.invoke_stage_b_build_app(
        n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    binding = next(value for value in boundary._CAPTURE_BINDINGS.values()
                   if value.application is application)
    session = binding.session
    assert binding.state == "ELIGIBLE"
    root_call = next(call for call in calls
                     if call[2] is None and call[1] & os.O_DIRECTORY)
    graph_calls = [root_call, *(call for call in calls if call[2] is not None)]
    assert len(graph_calls) == len(projection._GRAPH)
    assert Path(graph_calls[0][0]).resolve() == n4a_lineage["root"].resolve()
    assert graph_calls[0][2] is None
    assert graph_calls[0][1] & os.O_NOFOLLOW
    assert graph_calls[0][1] & os.O_DIRECTORY
    acquired_fds = {entry.index: entry.fd for entry in session.entries}
    def assert_directory_relative(call):
        assert call[2] is not None, "directory-relative open was omitted"
    for index, (parent_index, name, kind, role) in enumerate(projection._GRAPH[1:], start=1):
        path, flags, parent_fd = graph_calls[index]
        expected_name = session.generation if role == "generation" else name
        assert path == expected_name, f"{role} did not use a single descendant name"
        assert_directory_relative(graph_calls[index])
        assert parent_fd == acquired_fds[parent_index], f"{role} was not opened relative to its exact parent"
        assert flags & os.O_NOFOLLOW, f"{role} open omitted O_NOFOLLOW"
        if kind == "directory":
            assert flags & os.O_DIRECTORY, f"{role} directory open omitted O_DIRECTORY"
    assert not any(Path(path).is_absolute() for path, _, _ in graph_calls[1:])

    # The oracle must reject a path-based/lstat-then-open mutant that drops the
    # directory-relative argument even if its path happens to name the same file.
    with pytest.raises(AssertionError, match="directory-relative"):
        assert_directory_relative(("Contents", os.O_RDONLY, None))


def test_capture_nofollow_applies_at_the_actual_descendant_open_boundary(
        n4a_lineage, monkeypatch):
    projection = _projection_module()
    boundary = importlib.import_module(
        "gate0.feasibility.macos_stage_b_evidence_boundary",
    )
    real_open = os.open
    real_rename = os.rename
    attempted = []
    saved_contents = n4a_lineage["build_context"].sealed_destination.application_path / "Contents"
    saved_edge = saved_contents.with_name("Contents.pre-open")
    app_files = {}

    def observed_open(path, flags, *args, **kwargs):
        if path == "Contents" and kwargs.get("dir_fd") is not None:
            attempted.append((path, flags, kwargs["dir_fd"]))
            real_rename(saved_contents, saved_edge)
            saved_contents.symlink_to(saved_edge, target_is_directory=True)
        return real_open(path, flags, *args, **kwargs)

    def fake_process(s2, build_context, private_s2_file, env):
        write_capture_bundle(build_context.sealed_destination.application_path)
        app_files.update({p: p.read_bytes() for p in build_context.sealed_destination.application_path.rglob("*")
                          if p.is_file()})
        return subprocess.CompletedProcess(("synthetic",), 0, b"", b"")

    monkeypatch.setattr(os, "open", observed_open)
    monkeypatch.setattr(os, "supports_dir_fd", set(os.supports_dir_fd) | {observed_open})
    monkeypatch.setattr(boundary, "_run_stage_b_build_process", fake_process)
    application = boundary.invoke_stage_b_build_app(
        n4a_lineage["s2"], n4a_lineage["build_context"],
    )
    binding = next(value for value in boundary._CAPTURE_BINDINGS.values()
                   if value.application is application)
    try:
        assert len(attempted) == 1
        assert attempted[0][1] & os.O_NOFOLLOW
        assert attempted[0][1] & os.O_DIRECTORY
        assert binding.state == "REFUSED"
        assert binding.session is not None and binding.session.released
        assert binding.session.entries == []
        assert {p: p.read_bytes() for p in app_files} == app_files
        with pytest.raises(EvidenceDagError):
            boundary._begin_capture(application)
    finally:
        if saved_contents.is_symlink():
            saved_contents.unlink()
            real_rename(saved_edge, saved_contents)


def test_capture_exact_registered_application_and_bytes(capture_registered):
    case = capture_registered
    projection = _projection_module()
    capture = getattr(projection, "capture_signed_image_projection_source", None)
    assert capture is not None, "Task-3 capture API is absent"
    assert tuple(inspect.signature(capture).parameters) == ("application",)
    source = capture(case["application"])
    assert source.source_application is case["application"]
    assert source.repository_context is case["context"]
    assert source.generation_identity == case["context"].generation_identity
    for name, expected in case["expected"].items():
        assert getattr(source, name) == expected
    assert all(type(getattr(source, name)) is bytes for name in case["expected"]
               if name.endswith("_bytes"))
    assert tuple(slot for slot, _ in source.special_slot_state) == (-1, -2, -3, -4, -5, -6, -7)
    assert source.special_slot_state[3][1] == bytes(32)
    assert source.special_slot_state[5][1] == bytes(32)
    assert type(source.code_directory_identity.code_slot_sha256) is tuple
    assert type(source.code_directory_identity.special_slot_sha256) is tuple
    assert source._capture_registration is case["binding"].registration_token
    assert case["binding"].session.released
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])


@pytest.mark.parametrize("impostor_kind", (
    "copy", "equal_reconstruction", "forged_token", "stale_generation",
    "cross_context", "other_invocation", "mismatched_subject",
))
def test_capture_impostor_refuses_without_consuming_origin(capture_registered, impostor_kind):
    case = capture_registered
    projection = _projection_module()
    capture = getattr(projection, "capture_signed_image_projection_source", None)
    assert capture is not None, "Task-3 capture API is absent"
    original = case["application"]
    if impostor_kind == "copy":
        impostor = copy.copy(original)
    elif impostor_kind == "equal_reconstruction":
        impostor = replace(original)
    elif impostor_kind == "forged_token":
        impostor = replace(original, _registration_token=object())
    elif impostor_kind == "stale_generation":
        impostor = replace(original, _generation_identity="0" * 64)
    elif impostor_kind == "cross_context":
        impostor = replace(original, _repository_context_token=object())
    elif impostor_kind == "other_invocation":
        impostor = replace(original, _lifecycle_token=object())
    else:
        impostor = replace(original, _subject_path=Path(original._subject_path) / "elsewhere")
    with pytest.raises(EvidenceDagError):
        capture(impostor)
    assert not case["binding"].session.released
    assert not case["trace"]["reads"]
    source = capture(original)
    assert source.source_application is original


def test_capture_executable_acquired_once_no_fallback(capture_registered, monkeypatch):
    case = capture_registered
    projection = _projection_module()
    capture = getattr(projection, "capture_signed_image_projection_source", None)
    assert capture is not None, "Task-3 capture API is absent"
    executable_fd = case["binding"].session.role_fds["executable"]
    real_open = projection.os.open
    def forbid_executable_reopen(path, flags, *args, **kwargs):
        if path in {"StageBSandboxRunner", "Info.plist", "CodeResources"}:
            raise AssertionError("capture attempted physical-input path fallback")
        return real_open(path, flags, *args, **kwargs)
    monkeypatch.setattr(projection.os, "open", forbid_executable_reopen)
    source = capture(case["application"])
    for name in (
        "executable_code_region_bytes", "superblob_index_bytes", "code_directory_bytes",
        "entitlements_blob_bytes", "der_entitlements_blob_bytes",
        "requirements_blob_sha256", "cms_signature_blob_sha256",
    ):
        assert getattr(source, name) == case["expected"][name]
    assert case["trace"]["reads"].count(executable_fd) >= 1
    assert case["trace"]["origin_fds"].count(executable_fd) == 1


def test_capture_short_reads_complete_once(capture_registered, monkeypatch):
    case = capture_registered
    projection = _projection_module()
    capture = getattr(projection, "capture_signed_image_projection_source", None)
    assert capture is not None, "Task-3 capture API is absent"
    executable_fd = case["binding"].session.role_fds["executable"]
    original_read = projection.os.read
    monkeypatch.setattr(projection.os, "read", lambda fd, size: original_read(fd, min(size, 7)))
    source = capture(case["application"])
    assert source.info_plist_bytes == case["expected"]["info_plist_bytes"]
    assert source.code_directory_bytes == case["expected"]["code_directory_bytes"]
    assert case["trace"]["reads"].count(executable_fd) > 1
    assert case["trace"]["origin_fds"].count(executable_fd) == 1
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])


@pytest.mark.parametrize(("failure", "role"), [
    (failure, role)
    for failure in ("unreadable", "empty", "wrong_type", "short_eof",
                    "truncation", "inconsistency", "missing")
    for role in ("executable", "info_plist", "code_resources")
] + [("read_exception", "executable"), ("extraction_exception", "executable"),
     ("malformed_header", "executable"), *( (f"wrong_blob_magic_{slot}", "executable")
        for slot in (2, 5, 7, 0x10000) )])
def test_capture_io_and_extraction_fail_closed(capture_registered, monkeypatch, failure, role):
    case = capture_registered
    projection = _projection_module()
    capture = getattr(projection, "capture_signed_image_projection_source", None)
    assert capture is not None, "Task-3 capture API is absent"
    paths = {
        "executable": case["application"]._subject_path / "Contents/MacOS/StageBSandboxRunner",
        "info_plist": case["application"]._subject_path / "Contents/Info.plist",
        "code_resources": case["application"]._subject_path / "Contents/_CodeSignature/CodeResources",
    }
    if failure == "extraction_exception":
        if role != "executable":
            return
        monkeypatch.setattr(projection, "_extract_source_fields",
                            lambda *args: (_ for _ in ()).throw(ValueError("synthetic malformed image")))
    elif failure == "read_exception":
        if role != "executable":
            return
        original_read = projection.os.read
        failed = False
        def fail_once(fd, size):
            nonlocal failed
            if not failed:
                failed = True
                raise OSError(5, "synthetic read failure")
            return original_read(fd, size)
        monkeypatch.setattr(projection.os, "read", fail_once)
    elif failure == "unreadable":
        target_fd = case["binding"].session.role_fds[role]
        original_read = projection.os.read
        def deny_target(fd, size):
            if fd == target_fd:
                raise PermissionError(13, "synthetic EACCES")
            return original_read(fd, size)
        monkeypatch.setattr(projection.os, "read", deny_target)
    elif failure in {"empty", "truncation"}:
        paths[role].write_bytes(b"")
    elif failure == "wrong_type":
        saved = paths[role].with_name(paths[role].name + ".saved")
        paths[role].rename(saved)
        paths[role].mkdir()
    elif failure == "missing":
        paths[role].unlink()
    elif failure == "malformed_header":
        if role != "executable":
            return
        paths[role].write_bytes(b"\xcf\xfa\xed\xfe")
    elif failure.startswith("wrong_blob_magic_"):
        pass  # The trusted synthetic producer built this malformed typed blob before registration.
    elif failure == "short_eof":
        target_fd = case["binding"].session.role_fds[role]
        original_read = projection.os.read
        sent = False
        def eof_target(fd, size):
            nonlocal sent
            if fd == target_fd and not sent:
                sent = True
                return b""
            return original_read(fd, size)
        monkeypatch.setattr(projection.os, "read", eof_target)
    elif failure == "inconsistency":
        target_fd = case["binding"].session.role_fds[role]
        original_fstat = projection.os.fstat
        calls = 0
        def inconsistent_fstat(fd):
            nonlocal calls
            value = original_fstat(fd)
            if fd == target_fd:
                calls += 1
                if calls == 2:
                    changed_stat = list(value)
                    changed_stat[6] += 1
                    return os.stat_result(changed_stat)
            return value
        monkeypatch.setattr(projection.os, "fstat", inconsistent_fstat)
    with pytest.raises(EvidenceDagError):
        capture(case["application"])
    assert case["binding"].state == "REFUSED"
    assert case["binding"].session.released
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])


def test_capture_origin_lifetime_cannot_be_reconstructed(capture_registered):
    case = capture_registered
    projection = _projection_module()
    boundary = case["boundary"]
    capture = projection.capture_signed_image_projection_source
    original_fds = tuple(case["binding"].session.descriptors)
    projection._release_origin_graph(case["binding"].session)
    assert case["binding"].session.released
    assert case["binding"].state == "REFUSED", "premature private release did not poison capture eligibility"
    _replace_capture_edge_with_identical_copy(case, "Contents")
    with pytest.raises(EvidenceDagError):
        capture(case["application"])
    assert case["binding"].state == "REFUSED"
    assert not case["trace"]["reads"]
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])
    for fd in original_fds:
        with pytest.raises(OSError):
            os.fstat(fd)


@pytest.mark.parametrize(
    "edge",
    ("build", "generation", "application", "Contents", "MacOS", "_CodeSignature",
     "executable", "info_plist", "code_resources"),
)
@pytest.mark.parametrize("phase", ("before_read", "before_publish"))
def test_capture_byte_identical_replacement_refuses(capture_registered, monkeypatch, edge, phase):
    case = capture_registered
    projection = _projection_module()
    boundary = case["boundary"]
    original_path = _capture_edge_paths(case)[edge]
    original_manifest = _path_content_manifest(original_path)
    session = case["binding"].session
    original_entries = tuple(session.entries)
    replaced = {}

    def install_copy():
        path = _capture_edge_paths(case)[edge]
        saved = _replace_capture_edge_with_identical_copy(case, edge)
        replaced["saved"] = saved
        assert _path_content_manifest(saved) == original_manifest
        assert _path_content_manifest(path) == original_manifest
        assert path.lstat().st_ino != saved.lstat().st_ino
        if edge in {"build", "generation", "application", "Contents", "MacOS", "_CodeSignature"}:
            assert path.is_dir() and saved.is_dir()
        else:
            assert path.is_file() and saved.is_file()
        for entry in original_entries:
            held = os.fstat(entry.fd)
            assert (held.st_dev, held.st_ino, stat.S_IFMT(held.st_mode)) == entry.identity
            if entry.kind == "file":
                assert os.pread(entry.fd, 1, 0)

    if phase == "before_read":
        original_begin = boundary._begin_capture

        def replace_after_capture_begins(application):
            binding = original_begin(application)
            assert binding is case["binding"]
            assert case["trace"]["reads"] == []
            install_copy()
            return binding

        monkeypatch.setattr(boundary, "_begin_capture", replace_after_capture_begins)
    else:
        original_extract = projection._extract_source_fields

        def replace_after_retained_reads(*args):
            result = original_extract(*args)
            assert case["trace"]["reads"]
            assert set(case["trace"]["reads"]).issubset(set(session.role_fds.values()))
            install_copy()
            return result

        monkeypatch.setattr(projection, "_extract_source_fields", replace_after_retained_reads)

    with pytest.raises(EvidenceDagError):
        projection.capture_signed_image_projection_source(case["application"])
    assert case["binding"].state == "REFUSED"
    assert case["binding"].session.accepted is False
    assert replaced["saved"].exists()
    assert _path_content_manifest(_capture_edge_paths(case)[edge]) == original_manifest
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])
    for entry in original_entries:
        with pytest.raises(OSError):
            os.fstat(entry.fd)


@pytest.mark.parametrize(("malformed_case", "reason"), [
    ("duplicate_lc_code_signature", "duplicate or malformed"),
    ("signature_dataoff_before_commands", "signature extent is invalid"),
    ("signature_datasize_out_of_bounds", "signature extent is invalid"),
    ("superblob_offset_alias", "blob magic does not match its slot type"),
    ("superblob_partial_overlap", "embedded signature blobs overlap"),
    ("truncated_code_directory_hash_extent", "CodeDirectory slot extent is out of range"),
    ("unsupported_code_directory_version_next", "CodeDirectory parameters are unsupported or inconsistent"),
    ("unsupported_code_directory_version_future", "CodeDirectory parameters are unsupported or inconsistent"),
], ids=[
    "duplicate-lc-code-signature", "invalid-dataoff", "invalid-datasize",
    "superblob-offset-alias", "superblob-partial-overlap",
    "truncated-code-directory-hashes", "unsupported-next-code-directory-version",
    "unsupported-future-code-directory-version",
])
def test_capture_malformed_signed_image_refuses_without_publication(
        n4a_lineage, monkeypatch, malformed_case, reason):
    case = _register_malformed_capture(n4a_lineage, monkeypatch, malformed_case)
    before_tree = _synthetic_tree_manifest(case["root"])
    returned = []
    with pytest.raises(EvidenceDagError, match=reason):
        returned.append(
            case["projection"].capture_signed_image_projection_source(case["application"]),
        )
    assert returned == []
    assert case["binding"].state == "REFUSED"
    assert case["binding"].session.accepted is False
    assert case["binding"].session.released
    assert case["binding"].session.application is case["application"]
    assert case["boundary"]._CAPTURE_BINDINGS[id(case["application"])] is case["binding"]
    assert len(case["opened"]) == len(case["closed"])
    assert set(case["opened"]) == set(case["closed"])
    for fd in case["opened"]:
        with pytest.raises(OSError):
            os.fstat(fd)
    assert _synthetic_tree_manifest(case["root"]) == before_tree


@pytest.mark.parametrize("swap_after_role", ("executable", "info_plist"))
def test_capture_generation3_contents_swap_refuses(capture_registered, monkeypatch, swap_after_role):
    case = capture_registered
    projection = _projection_module()
    target_fd = case["binding"].session.role_fds[swap_after_role]
    physical_fds = set(case["binding"].session.role_fds.values())
    original_read = projection.os.read
    target_bytes = os.fstat(target_fd).st_size
    read_bytes = 0
    swapped = False
    def swap_after_executable(fd, size):
        nonlocal read_bytes, swapped
        data = original_read(fd, size)
        if fd == target_fd:
            read_bytes += len(data)
            if read_bytes == target_bytes and not swapped:
                swapped = True
                _replace_capture_edge_with_identical_copy(case, "Contents")
        return data
    monkeypatch.setattr(projection.os, "read", swap_after_executable)
    with pytest.raises(EvidenceDagError):
        projection.capture_signed_image_projection_source(case["application"])
    assert swapped
    assert set(case["trace"]["reads"]).issubset(physical_fds)
    assert case["binding"].state == "REFUSED"
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])


@pytest.mark.parametrize("phase", ("before_read", "before_publish"))
@pytest.mark.parametrize("edge", ("root", "build", "generation", "application", "Contents", "MacOS",
                                  "_CodeSignature", "executable", "info_plist", "code_resources"))
def test_capture_full_namespace_boundary_refuses(capture_registered, monkeypatch, phase, edge):
    case = capture_registered
    projection = _projection_module()
    boundary = case["boundary"]
    if phase == "before_read":
        _detach_capture_edge(case, edge)
    else:
        original_extract = projection._extract_source_fields
        def detach_after_extract(*args):
            fields_value = original_extract(*args)
            _detach_capture_edge(case, edge)
            return fields_value
        monkeypatch.setattr(projection, "_extract_source_fields", detach_after_extract)
    with pytest.raises(EvidenceDagError):
        projection.capture_signed_image_projection_source(case["application"])
    assert case["binding"].state == "REFUSED"
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])


@pytest.mark.parametrize("failure", (
    "read_exception", "extract_exception", "premature_release",
    *(f"close_error_{n}" for n in range(1, 11)),
))
def test_capture_descriptor_cleanup_all_terminal_paths(capture_registered, monkeypatch, failure):
    case = capture_registered
    projection = _projection_module()
    if failure == "read_exception":
        original_read = projection.os.read
        failed = False
        def fail_read_once(fd, size):
            nonlocal failed
            if not failed:
                failed = True
                raise OSError(5, "synthetic read error")
            return original_read(fd, size)
        monkeypatch.setattr(projection.os, "read", fail_read_once)
    elif failure == "extract_exception":
        monkeypatch.setattr(projection, "_extract_source_fields",
                            lambda *args: (_ for _ in ()).throw(ValueError("synthetic extraction failure")))
    elif failure == "premature_release":
        original_read = projection.os.read
        released = False
        def release_after_read(fd, size):
            nonlocal released
            data = original_read(fd, size)
            if not released:
                released = True
                projection._release_origin_graph(case["binding"].session)
            return data
        monkeypatch.setattr(projection.os, "read", release_after_read)
    else:
        original_close = projection.os.close
        ordinal = 0
        fail_at = int(failure.rsplit("_", 1)[1])
        def close_then_report_once(fd):
            nonlocal ordinal
            ordinal += 1
            original_close(fd)
            if ordinal == fail_at:
                raise OSError("synthetic close error after real close")
        monkeypatch.setattr(projection.os, "close", close_then_report_once)
    with pytest.raises(EvidenceDagError):
        projection.capture_signed_image_projection_source(case["application"])
    assert case["binding"].state == "REFUSED"
    assert case["trace"]["closed_origin_fds"]
    assert set(case["trace"]["closed_origin_fds"]) == set(case["trace"]["origin_fds"])
    for fd in case["trace"]["origin_fds"]:
        with pytest.raises(OSError):
            os.fstat(fd)


def test_capture_unresolved_close_retains_uncertain_descriptor_without_retry(
        capture_registered, monkeypatch):
    case = capture_registered
    projection = _projection_module()
    real_close = os.close
    uncertain_fd = case["binding"].session.role_fds["executable"]
    close_calls = []

    def fail_without_closing_selected_fd(fd):
        close_calls.append(fd)
        if fd == uncertain_fd:
            raise OSError("synthetic close failure before release")
        return real_close(fd)

    monkeypatch.setattr(projection.os, "close", fail_without_closing_selected_fd)
    try:
        with pytest.raises(EvidenceDagError):
            projection.capture_signed_image_projection_source(case["application"])
        session = case["binding"].session
        assert case["binding"].state == "REFUSED"
        assert not session.released
        assert session.release_attempted
        assert session.refusal_reason is not None and "cleanup" in session.refusal_reason
        assert [entry.fd for entry in session.entries] == [uncertain_fd]
        assert session.role_fds == {"executable": uncertain_fd}
        assert close_calls.count(uncertain_fd) == 1
        assert os.fstat(uncertain_fd).st_size > 0
        assert set(close_calls) == set(case["trace"]["origin_fds"])
        assert all(fd != uncertain_fd for fd in case["trace"]["closed_origin_fds"])
        for fd in case["trace"]["origin_fds"]:
            if fd == uncertain_fd:
                continue
            with pytest.raises(OSError):
                os.fstat(fd)
        assert case["trace"]["origin_fds"]
        assert not session.released
    finally:
        real_close(uncertain_fd)


def test_capture_retained_values_and_privacy_closed(capture_registered):
    case = capture_registered
    projection = _projection_module()
    source = projection.capture_signed_image_projection_source(case["application"])
    names = tuple(item.name for item in fields(source))
    assert names == (
        "source_application", "generation_identity", "repository_context",
        "executable_code_region_bytes", "info_plist_bytes", "code_resources_bytes",
        "superblob_index_bytes", "code_directory_bytes", "entitlements_blob_bytes",
        "der_entitlements_blob_bytes", "requirements_blob_sha256", "cms_signature_blob_sha256",
        "special_slot_state", "code_directory_identity", "_capture_registration",
    )
    retained = {name: getattr(source, name) for name in names if name.endswith("_bytes")}
    slots = source.special_slot_state
    cd_identity = source.code_directory_identity
    app = case["application"]._subject_path
    (app / "Contents/MacOS/StageBSandboxRunner").write_bytes(b"post-capture executable edit")
    (app / "Contents/Info.plist").write_bytes(b"raw test-only post-capture edit")
    (app / "Contents/_CodeSignature/CodeResources").write_bytes(b"another post-capture edit")
    assert retained == {name: getattr(source, name) for name in retained}
    assert slots == source.special_slot_state
    assert cd_identity == source.code_directory_identity
    assert all(type(value) is bytes for value in retained.values())
    public_bytes = b"\n".join(retained.values())
    assert b"SYNTHETIC_REQUIREMENTS_PREIMAGE" not in public_bytes
    assert b"SYNTHETIC_CMS_PREIMAGE" not in public_bytes
    assert case["trace"]["closed_origin_fds"]


def test_capture_frozen_fixture_and_guarantee_limits():
    blob = "d3d7a4611e375317e651049bceb345fe0d879744"
    result = subprocess.run(("git", "show", blob), check=True, stdout=subprocess.PIPE)
    document = result.stdout.decode("utf-8")
    match = re.search(r"### Canonical fixture vector\s+[^\n]*\n\s*```json\n([^\n]+)\n```", document)
    assert match is not None
    raw = match.group(1).encode("utf-8")
    assert len(raw) == 2110
    assert hashlib.sha256(raw).hexdigest() == "44391c8f9e0bde48dd2a5738526428f993056e7bf1a3a211f2f9def8b78ec310"
    vector = json.loads(raw)
    assert len(vector["members"]) == 8
    assert vector["source_member_mapping"]["executable_code_region"].endswith("@[0,codeLimit)")
    projection_source = _projection_module()
    source_text = Path(projection_source.__file__).read_text(encoding="utf-8").lower()
    assert not any(term in source_text for term in (
        "kqueue", "vnode", "privileged_snapshot", "hostile_writer", "universal_history",
    ))


def test_task4_handoff_preserves_retained_aliases_without_recapture(
        capture_registered, monkeypatch):
    """Task 4 must hand off exact Task-3 values without reopening or reparsing."""
    from gate0.feasibility.macos_stage_b_evidence_constants import N4ABoundaryPrimitive

    projection = _projection_module()
    case = capture_registered
    source = projection.capture_signed_image_projection_source(case["application"])
    primitive = N4ABoundaryPrimitive("N4A_BOUNDARY_V1", "1" * 64, 1, "2" * 64, 2)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Task 4 re-entered Task-3 capture/parser work")

    monkeypatch.setattr(projection, "capture_signed_image_projection_source", forbidden)
    monkeypatch.setattr(projection, "_read_complete_physical_input", forbidden)
    monkeypatch.setattr(projection, "_extract_source_fields", forbidden)
    for name in ("open", "read", "stat", "fstat"):
        monkeypatch.setattr(os, name, forbidden)
    monkeypatch.setattr(projection.hashlib, "sha256", forbidden)
    parsed = projection._parse_signed_image_projection_source(source, primitive)

    assert parsed.source is source
    assert parsed.measured_primitive is primitive
    assert parsed.source_application is source.source_application
    assert parsed.repository_context is source.repository_context
    assert parsed.generation_identity is source.generation_identity
    for name in (
        "executable_code_region_bytes", "info_plist_bytes", "code_resources_bytes",
        "superblob_index_bytes", "code_directory_bytes", "entitlements_blob_bytes",
        "der_entitlements_blob_bytes", "requirements_blob_sha256",
        "cms_signature_blob_sha256", "special_slot_state", "code_directory_identity",
    ):
        assert getattr(parsed, name) is getattr(source, name)


@pytest.mark.parametrize("bad_input", ("source", "primitive"))
def test_task4_requires_exact_source_and_primitive_types(capture_registered, bad_input):
    from gate0.feasibility.macos_stage_b_evidence_constants import (
        EvidenceDagError, N4ABoundaryPrimitive,
    )

    projection = _projection_module()
    source = projection.capture_signed_image_projection_source(
        capture_registered["application"],
    )
    primitive = N4ABoundaryPrimitive("N4A_BOUNDARY_V1", "1" * 64, 1, "2" * 64, 2)
    args = (object(), primitive) if bad_input == "source" else (source, object())
    with pytest.raises(EvidenceDagError):
        projection._parse_signed_image_projection_source(*args)


@pytest.mark.parametrize("malformation", (
    "mutable_byte_member", "bad_index_length", "uppercase_requirements_digest",
    "missing_slot", "duplicate_slot", "reordered_slot", "boolean_code_limit",
    "non_tuple_code_slots", "missing_code_slots", "reordered_identity_slot",
    "digest_on_structural_zero", "requirements_cross_field_mismatch",
    "malformed_cms_digest", "non_string_generation", "nonzero_structural_zero_slot",
))
def test_task4_refuses_malformed_retained_value_shapes(capture_registered, malformation):
    from dataclasses import replace

    from gate0.feasibility.macos_stage_b_evidence_constants import (
        EvidenceDagError, N4ABoundaryPrimitive,
    )

    projection = _projection_module()
    source = projection.capture_signed_image_projection_source(
        capture_registered["application"],
    )
    slots = source.special_slot_state
    identity = source.code_directory_identity
    if malformation == "mutable_byte_member":
        source = replace(source, info_plist_bytes=bytearray(source.info_plist_bytes))
    elif malformation == "bad_index_length":
        source = replace(source, superblob_index_bytes=source.superblob_index_bytes[:-1])
    elif malformation == "uppercase_requirements_digest":
        source = replace(source, requirements_blob_sha256=source.requirements_blob_sha256.upper())
    elif malformation == "missing_slot":
        source = replace(source, special_slot_state=slots[:-1])
    elif malformation == "duplicate_slot":
        source = replace(source, special_slot_state=(slots[0], slots[0], *slots[2:]))
    elif malformation == "reordered_slot":
        source = replace(source, special_slot_state=(slots[1], slots[0], *slots[2:]))
    elif malformation == "boolean_code_limit":
        source = replace(source, code_directory_identity=replace(identity, code_limit=True))
    elif malformation == "non_tuple_code_slots":
        source = replace(source, code_directory_identity=replace(
            identity, code_slot_sha256=list(identity.code_slot_sha256),
        ))
    elif malformation == "missing_code_slots":
        source = replace(source, code_directory_identity=replace(
            identity, code_slot_sha256=None,
        ))
    elif malformation == "reordered_identity_slot":
        special = identity.special_slot_sha256
        source = replace(source, code_directory_identity=replace(
            identity, special_slot_sha256=(special[1], special[0], *special[2:]),
        ))
    elif malformation == "digest_on_structural_zero":
        special = identity.special_slot_sha256
        source = replace(source, code_directory_identity=replace(
            identity, special_slot_sha256=(*special[:3], (-4, "a" * 64), *special[4:]),
        ))
    elif malformation == "requirements_cross_field_mismatch":
        source = replace(source, requirements_blob_sha256="f" * 64)
    elif malformation == "malformed_cms_digest":
        source = replace(source, cms_signature_blob_sha256="A" * 64)
    elif malformation == "non_string_generation":
        source = replace(source, generation_identity=1)
    elif malformation == "nonzero_structural_zero_slot":
        malformed = list(slots)
        malformed[3] = (-4, b"x" * 32)
        source = replace(source, special_slot_state=tuple(malformed))

    primitive = N4ABoundaryPrimitive("N4A_BOUNDARY_V1", "1" * 64, 1, "2" * 64, 2)
    with pytest.raises(EvidenceDagError):
        projection._parse_signed_image_projection_source(source, primitive)


def _task5_projection(case):
    from gate0.feasibility.macos_stage_b_evidence_constants import N4ABoundaryPrimitive

    projection = _projection_module()
    source = projection.capture_signed_image_projection_source(case["application"])
    primitive = N4ABoundaryPrimitive(
        "N4A_BOUNDARY_PRIMITIVE_V1", "1" * 64, 1, "2" * 64, 2,
    )
    projector = getattr(projection, "project_signed_image", None)
    assert callable(projector), "Task-5 public projection is absent"
    return projection, source, primitive, projector(source, primitive)


def test_projected_members_match_retained_source_bytes(capture_registered):
    _, source, _, projected = _task5_projection(capture_registered)
    for name in (
        "executable_code_region_bytes", "info_plist_bytes", "code_resources_bytes",
        "superblob_index_bytes", "code_directory_bytes", "entitlements_blob_bytes",
        "der_entitlements_blob_bytes",
    ):
        assert getattr(projected, name) is getattr(source, name)
    assert projected.requirements_blob_sha256 is source.requirements_blob_sha256
    assert projected.cms_signature_blob_sha256 is source.cms_signature_blob_sha256
    assert projected.special_slot_state is source.special_slot_state
    assert projected.signing_time_stable_code_directory_identity is source.code_directory_identity


def test_projected_requirements_and_cms_preimages_are_elided(capture_registered):
    _, _, _, projected = _task5_projection(capture_registered)
    retained_bytes = b"".join((
        projected.executable_code_region_bytes, projected.info_plist_bytes,
        projected.code_resources_bytes, projected.superblob_index_bytes,
        projected.code_directory_bytes, projected.entitlements_blob_bytes,
        projected.der_entitlements_blob_bytes, projected.canonical_identity_json_bytes,
    ))
    assert b"SYNTHETIC_REQUIREMENTS_PREIMAGE" not in retained_bytes
    assert b"SYNTHETIC_CMS_PREIMAGE" not in retained_bytes
    assert len(projected.requirements_blob_sha256) == 64
    assert len(projected.cms_signature_blob_sha256) == 64


def test_identity_json_literal_fixture_bytes_and_sha256():
    projection = _projection_module()
    serializer = getattr(projection, "_serialize_canonical_identity_json", None)
    assert callable(serializer), "Task-5 closed canonical serializer is absent"
    document = json.loads(CANONICAL_IDENTITY_JSON_FIXTURE)
    assert serializer(document) == CANONICAL_IDENTITY_JSON_FIXTURE
    assert len(CANONICAL_IDENTITY_JSON_FIXTURE) == 2110
    assert hashlib.sha256(CANONICAL_IDENTITY_JSON_FIXTURE).hexdigest() == (
        "44391c8f9e0bde48dd2a5738526428f993056e7bf1a3a211f2f9def8b78ec310"
    )
    assert not CANONICAL_IDENTITY_JSON_FIXTURE.startswith(b"\xef\xbb\xbf")
    assert not CANONICAL_IDENTITY_JSON_FIXTURE.endswith(b"\n")


def test_projection_fixture_does_not_supply_expected_values_to_verifier(capture_registered):
    # Fixed hashes and lengths are independent oracles for the frozen synthetic
    # vector. Poison the fixture's own expected map so it cannot drive the check.
    independent_source_oracle = {
        "executable_code_region_bytes": (512, "114ffbeaef8a50f402bdb9a8dc9a18497e82adc5c072701666890cc9f027419a"),
        "info_plist_bytes": (57, "4b902f1c8327204f4973a0e2b62cae9534846d3b9f76bdcc508e83964301100c"),
        "code_resources_bytes": (86, "dde7dbcf98756467af0a8a1482922a1fcd750022064fff9f4551d150bd6cbe53"),
        "superblob_index_bytes": (52, "a4374711157c7b2af66b3e9d8f6e931c7b0d17f2c5e7f34ee3b4e70d6aa47aef"),
        "code_directory_bytes": (310, "373327ac0c65f4d75918b5edb17325d70fd548af83adb93ee422b3a894d6de45"),
        "entitlements_blob_bytes": (65, "d87923ce17ec6f107d8ac9683ecdffe2bf722bff75a236ed99546f4c6178be86"),
        "der_entitlements_blob_bytes": (10, "5ee70472dc60a1de31b1fb41a2bc18eb7fa3ef99fe43e714e2ad8bb3dbf2b0bc"),
    }
    independent_digest_oracle = {
        "requirements_blob_sha256": "08dd17999a02956f1f91fd6bad0024b5cc314dd2f22174d6e00d71a2b9bbd2bf",
        "cms_signature_blob_sha256": "7b37a9312103a8a1f0c61ada45e14cadf2b44d8fadfab387fa2e4605c03487f4",
    }
    capture_registered["expected"].clear()
    _, source, _, projected = _task5_projection(capture_registered)
    for name, (octets, digest) in independent_source_oracle.items():
        value = getattr(projected, name)
        assert value is getattr(source, name)
        assert len(value) == octets
        assert hashlib.sha256(value).hexdigest() == digest
    for name, digest in independent_digest_oracle.items():
        assert getattr(projected, name) == digest


def test_identity_json_repeat_serialization_is_identical(capture_registered):
    _, source, primitive, first = _task5_projection(capture_registered)
    projection = _projection_module()
    second = projection.project_signed_image(source, primitive)
    assert second.canonical_identity_json_bytes == first.canonical_identity_json_bytes


def test_manifest_expected_bytes_are_independent_literal():
    projection = _projection_module()
    serializer = getattr(projection, "_serialize_canonical_identity_json", None)
    assert callable(serializer), "Task-5 closed canonical serializer is absent"
    independent_literal = CANONICAL_IDENTITY_JSON_FIXTURE
    assert len(independent_literal) == 2110
    assert hashlib.sha256(independent_literal).hexdigest() == (
        "44391c8f9e0bde48dd2a5738526428f993056e7bf1a3a211f2f9def8b78ec310"
    )
    assert serializer(json.loads(independent_literal)) == independent_literal


def test_identity_json_rejects_missing_extra_duplicate_and_wrong_type_fields():
    projection = _projection_module()
    serializer = getattr(projection, "_serialize_canonical_identity_json", None)
    assert callable(serializer), "Task-5 closed canonical serializer is absent"
    document = json.loads(CANONICAL_IDENTITY_JSON_FIXTURE)
    missing = {key: value for key, value in document.items() if key != "schema_version"}
    extra = {**document, "unexpected": "value"}
    duplicate = tuple((*document.items(), ("schema_version", document["schema_version"])))
    duplicate_nested = json.loads(CANONICAL_IDENTITY_JSON_FIXTURE)
    cd_pairs = tuple((*duplicate_nested["code_directory_identity"].items(),
                      ("sha256", duplicate_nested["code_directory_identity"]["sha256"])))
    duplicate_nested["code_directory_identity"] = cd_pairs
    wrong_type = json.loads(CANONICAL_IDENTITY_JSON_FIXTURE)
    wrong_type["code_directory_identity"]["code_limit"] = True
    wrong_code_slot_count = json.loads(CANONICAL_IDENTITY_JSON_FIXTURE)
    wrong_code_slot_count["code_directory_identity"]["code_slot_sha256"].append("3" * 64)
    for invalid in (missing, extra, duplicate, duplicate_nested, wrong_type,
                    wrong_code_slot_count):
        with pytest.raises(EvidenceDagError):
            serializer(invalid)


def test_missing_member_cannot_be_hidden_by_empty_fixture_default():
    projection = _projection_module()
    serializer = getattr(projection, "_serialize_canonical_identity_json", None)
    assert callable(serializer), "Task-5 closed canonical serializer is absent"
    independent_literal_document = json.loads(CANONICAL_IDENTITY_JSON_FIXTURE)
    malformed_documents = []
    missing = copy.deepcopy(independent_literal_document)
    del missing["members"]["identity"]
    malformed_documents.append(missing)
    empty = copy.deepcopy(independent_literal_document)
    empty["members"]["identity"] = ""
    malformed_documents.append(empty)
    null_value = copy.deepcopy(independent_literal_document)
    null_value["members"]["identity"] = None
    malformed_documents.append(null_value)
    for malformed in malformed_documents:
        with pytest.raises(EvidenceDagError):
            serializer(malformed)


def test_identity_json_contains_primitive_exactly_once(capture_registered):
    _, _, primitive, projected = _task5_projection(capture_registered)
    document = json.loads(projected.canonical_identity_json_bytes)
    assert tuple(document["n4a_boundary_primitive"]) == (
        "format", "renderer_input_octets", "renderer_input_sha256",
        "signer_entitlements_octets", "signer_entitlements_sha256",
    )
    assert document["n4a_boundary_primitive"] == {
        "format": primitive.format,
        "renderer_input_sha256": primitive.renderer_input_sha256,
        "renderer_input_octets": primitive.renderer_input_octets,
        "signer_entitlements_sha256": primitive.signer_entitlements_sha256,
        "signer_entitlements_octets": primitive.signer_entitlements_octets,
    }
    assert list(document).count("n4a_boundary_primitive") == 1


def test_identity_json_excludes_prohibited_values_and_post_b_identity(capture_registered):
    _, _, _, projected = _task5_projection(capture_registered)
    document = json.loads(projected.canonical_identity_json_bytes)
    assert tuple(document) == (
        "cms_signature_blob_sha256", "code_directory_identity", "members",
        "n4a_boundary_primitive", "requirements_blob_sha256", "schema_version",
        "source_member_mapping",
    )
    serialized = projected.canonical_identity_json_bytes
    for forbidden in (
        b"team_identifier", b"certificate_common_name", b"designated_requirement",
        b"personal_name", b"email", b"application_path", b"source_path",
        b"capture_registration", b"capability_token", b"registry", b"handoff_token",
        b"commit_sha", b"tree_sha", b"post_b", b"SYNTHETIC_REQUIREMENTS_PREIMAGE",
        b"SYNTHETIC_CMS_PREIMAGE",
    ):
        assert forbidden not in serialized
