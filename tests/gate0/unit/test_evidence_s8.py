"""WP-10 verifier-owned N5 S8 extraction regressions."""
from __future__ import annotations

import ast
import copy
import dataclasses
import hashlib
import inspect
import json
import os
import plistlib
import re
import struct
import subprocess
import threading
from pathlib import Path

import pytest

from gate0.feasibility import macos_stage_b_evidence_anchor as anchor_mod
from gate0.feasibility import macos_stage_b_evidence_boundary as boundary_mod
from gate0.feasibility import macos_stage_b_evidence_git as git_mod
from gate0.feasibility import macos_stage_b_evidence_seal as seal_mod
from gate0.feasibility import macos_stage_b_evidence_snapshot as snapshot_mod
from gate0.feasibility import macos_stage_b_evidence_s8 as s8_mod
from gate0.feasibility.macos_stage_b_evidence_constants import (
    AuthorityTuple,
    EvidenceDagError,
    EvidenceFailureCode,
    FrozenArtifact,
    ParsedEntitlementPolicy,
    S8Capture,
)


_READ_ONLY_KEY = "com.apple.security.temporary-exception.files.absolute-path.read-only"
_READ_WRITE_KEY = "com.apple.security.temporary-exception.files.absolute-path.read-write"
_FIXED_ROOT_NAMES = ("worktree", "worktree_src", "python", "python_runtime", "model", "synthetic", "ffmpeg", "ffprobe", "output")
_DEFAULT_ROOTS = {f"roots.{name}": f"/synthetic/{name}" for name in _FIXED_ROOT_NAMES}
_ALT_ROOTS = {f"roots.{name}": f"/synthetic-alt/{name}" for name in _FIXED_ROOT_NAMES}


def _module_functions():
    return {name: function for name, function in inspect.getmembers(s8_mod, inspect.isfunction)
            if function.__module__ == s8_mod.__name__}


def test_n5_extractor_signature_is_exactly_one_application():
    functions = _module_functions()
    public = sorted(name for name in functions if not name.startswith("_"))
    assert public == ["capture_and_evaluate_s8", "extract_s8_from_n4a_application"]
    extract = inspect.signature(functions["extract_s8_from_n4a_application"])
    assert list(extract.parameters) == ["application"]
    assert extract.parameters["application"].default is inspect.Parameter.empty
    assert list(inspect.signature(functions["capture_and_evaluate_s8"]).parameters) == ["application", "exact_s1", "seal"]
    mandated = {
        "_run_codesign_entitlements": ["application"],
        "_claim_n5_subject": ["application", "subject_path"],
        "_finish_n5_claim": ["token"],
        "_release_n5_claim": ["token"],
        "_resolve_registered_context": ["application"],
    }
    for name, parameters in mandated.items():
        assert list(inspect.signature(functions[name]).parameters) == parameters
    for name, function in functions.items():
        for parameter in inspect.signature(function).parameters.values():
            assert parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD), name
            if name not in mandated and name not in ("extract_s8_from_n4a_application", "capture_and_evaluate_s8"):
                assert not re.search(r"bundle|path|subject|destination|identity", parameter.name), (name, parameter.name)
    source = inspect.getsource(s8_mod)
    tree = ast.parse(source)
    assert not [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
    assert "import subprocess" in source and "import threading" in source


def _expected_policy_for(roots=None):
    roots = dict(_DEFAULT_ROOTS if roots is None else roots)
    reads = [roots[f"roots.{name}"] for name in _FIXED_ROOT_NAMES if name != "output"]
    read_only = sorted({path.rstrip("/") + "/" for path in reads})
    read_write = [roots["roots.output"].rstrip("/") + "/"]
    return ParsedEntitlementPolicy(True, tuple(read_only), tuple(read_write),
                                   ("com.apple.security.app-sandbox", _READ_ONLY_KEY, _READ_WRITE_KEY))


def _policy_payload(policy=None):
    policy = _expected_policy_for() if policy is None else policy
    return plistlib.dumps({
        "com.apple.security.app-sandbox": policy.app_sandbox,
        _READ_ONLY_KEY: list(policy.read_only_paths),
        _READ_WRITE_KEY: list(policy.read_write_paths),
    }, fmt=plistlib.FMT_XML, sort_keys=True)


def _bundle(entitlements_payload: bytes):
    info = b'<?xml version="1.0"?><plist version="1.0"><dict/></plist>'
    resources = b'<?xml version="1.0"?><plist version="1.0"><dict><key>files</key><dict/></dict></plist>'

    def blob(magic, payload):
        return struct.pack(">II", magic, 8 + len(payload)) + payload

    requirements = blob(0xFADE0C01, b"SYNTHETIC_REQUIREMENTS_PREIMAGE")
    entitlements = blob(0xFADE7171, entitlements_payload)
    der = blob(0xFADE7172, b"\x30\x00")
    cms = blob(0xFADE0B01, b"SYNTHETIC_CMS_PREIMAGE")
    ident = b"synthetic\x00"
    hash_offset = 44 + len(ident) + 7 * 32
    cd_length = hash_offset + 32
    signature_length = 52 + cd_length + sum(map(len, (requirements, entitlements, der, cms)))
    header = struct.pack("<IiiIIIII", 0xFEEDFACF, 0x0100000C, 0, 2, 1, 16, 0, 0)
    command = struct.pack("<IIII", 0x1D, 16, 512, signature_length)
    code = (header + command).ljust(512, b"\x00")
    special = {
        1: hashlib.sha256(info).digest(),
        2: hashlib.sha256(requirements).digest(),
        3: hashlib.sha256(resources).digest(),
        4: bytes(32),
        5: hashlib.sha256(entitlements).digest(),
        6: bytes(32),
        7: hashlib.sha256(der).digest(),
    }
    code_directory = struct.pack(">9I4BI", 0xFADE0C02, cd_length, 0x20001, 0, hash_offset, 44,
                                 7, 1, 512, 32, 2, 0, 12, 0)
    code_directory += ident + b"".join(special[i] for i in range(7, 0, -1))
    code_directory += hashlib.sha256(code).digest()
    blobs = ((0, code_directory), (2, requirements), (5, entitlements), (7, der), (0x10000, cms))
    offset = 52
    entries = []
    for kind, raw in blobs:
        entries.append(struct.pack(">II", kind, offset))
        offset += len(raw)
    index = struct.pack(">III", 0xFADE0CC0, offset, 5) + b"".join(entries)
    return code + index + b"".join(raw for _, raw in blobs)


def _write_bundle(application_path: Path, entitlements_payload: bytes):
    (application_path / "Contents/MacOS").mkdir(parents=True)
    (application_path / "Contents/_CodeSignature").mkdir()
    (application_path / "Contents/MacOS/StageBSandboxRunner").write_bytes(_bundle(entitlements_payload))
    info = b'<?xml version="1.0"?><plist version="1.0"><dict/></plist>'
    resources = b'<?xml version="1.0"?><plist version="1.0"><dict><key>files</key><dict/></dict></plist>'
    (application_path / "Contents/Info.plist").write_bytes(info)
    (application_path / "Contents/_CodeSignature/CodeResources").write_bytes(resources)


def _git(root: Path, *args):
    env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
    return subprocess.run(("git", *args), cwd=root, env=env, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()


def _build_lineage(root: Path, state: dict, *, ordinal: int, observed_payload: bytes,
                   embedded_payload: bytes | None = None, roots=None):
    root = Path(root).resolve()
    embedded_payload = observed_payload if embedded_payload is None else embedded_payload
    roots = dict(_DEFAULT_ROOTS if roots is None else roots)
    root.mkdir(parents=True)
    _git(root, "init", "-q")
    # Repo-local identity keeps anchor subprocesses hermetic: the anchor runs Git
    # with a scrubbed env, so host/user identity auto-detection must not be needed.
    _git(root, "config", "user.name", "test")
    _git(root, "config", "user.email", "test@example.invalid")
    _git(root, "checkout", "-q", "-b", "main")
    (root / "controller.json").write_bytes(b"{}")
    _git(root, "add", "controller.json")
    # A lineage-unique base commit keeps independently built synthetic lineages
    # distinct even when the product anchor commits them within the same
    # wall-clock second (Git commit timestamps have one-second resolution, and
    # a fast runner can build two lineages inside the same second).
    _git(root, "commit", "-q", "-m", f"base {root.name} {ordinal}")
    base = _git(root, "rev-parse", "HEAD")
    blob = _git(root, "hash-object", "controller.json")
    authority = AuthorityTuple(base, blob, blob, blob, ordinal)
    s1data = json.dumps({"roots": roots, "tool_dependency_roots": [], "python_dependency_roots": []},
                        sort_keys=True, separators=(",", ":")).encode()
    s1 = FrozenArtifact("S1", "S1.json", s1data, hashlib.sha256(s1data).hexdigest(), len(s1data))
    s2 = snapshot_mod.render_s2_from_s1(s1)
    empty = b"{}"
    s3 = FrozenArtifact("S3", "S3.json", empty, hashlib.sha256(empty).hexdigest(), len(empty))
    s4 = FrozenArtifact("S4", "S4.json", empty, hashlib.sha256(empty).hexdigest(), len(empty))
    state["holder"]["root"] = root
    state["embedded"] = embedded_payload
    state["payload"] = observed_payload
    anchor = anchor_mod.create_s7_anchor(base, (s1, s2, s3, s4))
    context = git_mod.verify_repository_context(authority, anchor.commit_sha)
    anchored_s1 = anchor_mod.resolve_anchored_s1(context, anchor)
    build_context = boundary_mod._create_verifier_owned_build_context(context, anchor)
    result = boundary_mod.measure_and_handoff_n4a(anchored_s1, s2, build_context)
    seal = seal_mod.seal_n4b(anchor, result.n4b_handoff)
    state["leaf_calls"].clear()
    return {"root": root, "generation": context.generation_identity, "context": context,
            "anchor": anchor, "s1": s1, "result": result, "seal": seal,
            "application": result.transient_application, "observed": observed_payload,
            "embedded": embedded_payload}


@pytest.fixture
def harness(tmp_path, monkeypatch):
    state = {"holder": {"root": None}, "payload": b"", "embedded": b"", "leaf_calls": [],
             "leaf": None, "leaf_response": None}
    monkeypatch.setattr(git_mod, "_discover_repository_root_from_module_location",
                        lambda: state["holder"]["root"])

    def fake_build(s2, build_context, private_s2_file, env):
        _write_bundle(Path(build_context.sealed_destination.application_path), state["embedded"])
        return subprocess.CompletedProcess(("synthetic-build",), 0, b"", b"")

    def fake_leaf(application):
        state["leaf_calls"].append(application)
        if state["leaf_response"] is not None:
            return state["leaf_response"]
        return subprocess.CompletedProcess(("synthetic-codesign",), 0, state["payload"], b"")

    monkeypatch.setattr(boundary_mod, "_run_stage_b_build_process", fake_build)
    monkeypatch.setattr(s8_mod, "_run_codesign_entitlements", fake_leaf)
    state["leaf"] = fake_leaf

    def build(name="lineage", **kwargs):
        return _build_lineage(tmp_path / name, state, **kwargs)

    state["build"] = build
    return state


def test_independent_synthetic_lineages_are_distinct_without_wall_clock_seconds(harness):
    # Two synthetic lineages built back-to-back must never be the same
    # generation. Git commit timestamps have one-second resolution, so a fast
    # runner previously produced identical base and anchor commit ids when two
    # lineages were built inside the same wall-clock second; the splice refusal
    # then observed "identical" generations and silently accepted the pair.
    payload = _policy_payload()
    first = harness["build"](name="distinct-a", ordinal=32, observed_payload=payload)
    second = harness["build"](name="distinct-b", ordinal=33, observed_payload=payload)
    assert first["anchor"].commit_sha != second["anchor"].commit_sha

    # Splice refusal still reports the S7-parent divergence rather than silently
    # accepting two "identical" generations.
    with pytest.raises(EvidenceDagError) as cross_seal:
        s8_mod.capture_and_evaluate_s8(first["application"], second["s1"], second["seal"])
    assert cross_seal.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
    assert "S7 parent" in cross_seal.value.reason
    assert not harness["leaf_calls"]

    third = harness["build"](name="distinct-c", ordinal=34, observed_payload=payload)
    anchors = [lineage["anchor"].commit_sha for lineage in (first, second, third)]
    evaluations = [lineage["context"].evaluation_commit for lineage in (first, second, third)]
    generations = [lineage["generation"] for lineage in (first, second, third)]
    assert len(set(anchors)) == 3
    assert len(set(evaluations)) == 3
    assert len(set(generations)) == 3


def test_n5_stdout_is_retained_without_decode_trim_or_reserialize(harness):
    observed = b"\x00\xff\xfe\r\n leading" + b"\xef\xbb\xbf" + b"no-trailing-newline\x00"
    lineage = harness["build"](name="bytes", ordinal=1, observed_payload=observed)
    extracted = s8_mod.extract_s8_from_n4a_application(lineage["application"])
    assert type(extracted) is bytes
    assert extracted == observed
    assert len(harness["leaf_calls"]) == 1
    with pytest.raises(EvidenceDagError) as consumed:
        s8_mod.extract_s8_from_n4a_application(lineage["application"])
    assert consumed.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
    assert "already consumed" in consumed.value.reason
    assert len(harness["leaf_calls"]) == 1
    for index, bad_result in enumerate((
        subprocess.CompletedProcess(("synthetic-codesign",), 1, b"", b""),
        subprocess.CompletedProcess(("synthetic-codesign",), 0, b"", b""),
        subprocess.CompletedProcess(("synthetic-codesign",), 0, "not-bytes", b""),
    )):
        observed_lineage = harness["build"](name=f"obs{index}", ordinal=6 + index,
                                            observed_payload=_policy_payload())
        harness["leaf_response"] = bad_result
        try:
            with pytest.raises(EvidenceDagError) as observation:
                s8_mod.extract_s8_from_n4a_application(observed_lineage["application"])
        finally:
            harness["leaf_response"] = None
        assert observation.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
        assert "NOT_OBSERVED:" in observation.value.reason
        assert len(harness["leaf_calls"]) == 1
        assert id(observed_lineage["application"]) not in s8_mod._N5_STATE
    assert s8_mod._run_codesign_entitlements is harness["leaf"]
    module_source = inspect.getsource(s8_mod)
    source_tree = ast.parse(module_source)
    run_calls = [node for node in ast.walk(source_tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                 and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"
                 and node.func.attr == "run"]
    leaf = next(node for node in source_tree.body if isinstance(node, ast.FunctionDef)
                and node.name == "_run_codesign_entitlements")
    assert len(run_calls) == 1 and run_calls[0] in ast.walk(leaf)
    assert "os.system" not in module_source and "shell=True" not in module_source


def _policy_dict(**overrides):
    policy = _expected_policy_for()
    value = {
        "com.apple.security.app-sandbox": policy.app_sandbox,
        _READ_ONLY_KEY: list(policy.read_only_paths),
        _READ_WRITE_KEY: list(policy.read_write_paths),
    }
    value.update(overrides)
    return plistlib.dumps(value, fmt=plistlib.FMT_XML, sort_keys=True)


def test_type_strict_boolean_true_is_not_integer_one(harness):
    assert s8_mod._parse_payload(_policy_payload()) == _expected_policy_for()
    for bad in (1, "true", False, []):
        with pytest.raises(EvidenceDagError) as error:
            s8_mod._parse_payload(_policy_dict(**{"com.apple.security.app-sandbox": bad}))
        assert error.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE

    lineage = harness["build"](
        name="sandbox-type", ordinal=28,
        observed_payload=_policy_dict(**{"com.apple.security.app-sandbox": 1}),
    )
    with pytest.raises(EvidenceDagError) as end_to_end:
        s8_mod.capture_and_evaluate_s8(lineage["application"], lineage["s1"], lineage["seal"])
    assert end_to_end.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    assert len(harness["leaf_calls"]) == 1


def test_type_strict_arrays_are_not_scalars(harness):
    expected = _expected_policy_for()
    assert s8_mod._parse_payload(_policy_payload()) == expected
    for bad in ("/single/path", ["/a", 1], [["/a"]], True):
        with pytest.raises(EvidenceDagError) as error:
            s8_mod._parse_payload(_policy_dict(**{_READ_ONLY_KEY: bad}))
        assert error.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    missing = {
        "com.apple.security.app-sandbox": True,
        _READ_ONLY_KEY: list(expected.read_only_paths),
    }
    with pytest.raises(EvidenceDagError) as error:
        s8_mod._parse_payload(plistlib.dumps(missing, fmt=plistlib.FMT_XML, sort_keys=True))
    assert error.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    widened = _policy_dict(**{_READ_ONLY_KEY: list(expected.read_only_paths) + ["/extra/"]})
    with pytest.raises(EvidenceDagError) as closure:
        s8_mod._require_closure(s8_mod._parse_payload(widened), expected)
    assert closure.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE

    lineage = harness["build"](
        name="paths-type", ordinal=29,
        observed_payload=_policy_dict(**{_READ_ONLY_KEY: "scalar"}),
    )
    with pytest.raises(EvidenceDagError) as end_to_end:
        s8_mod.capture_and_evaluate_s8(lineage["application"], lineage["s1"], lineage["seal"])
    assert end_to_end.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    assert len(harness["leaf_calls"]) == 1


def test_exact_renderer_array_order_is_required(harness):
    expected = _expected_policy_for()
    permuted = list(reversed(expected.read_only_paths))
    assert permuted != list(expected.read_only_paths)
    order_payload = _policy_dict(**{_READ_ONLY_KEY: permuted})
    with pytest.raises(EvidenceDagError) as closure:
        s8_mod._require_closure(s8_mod._parse_payload(order_payload), expected)
    assert closure.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    first = s8_mod._parse_payload(_policy_payload())
    second = s8_mod._parse_payload(_policy_dict(**{_READ_ONLY_KEY: permuted}))
    assert first != second
    malformed = json.dumps({
        "roots": {f"roots.{name}": (123 if name == "model" else f"/synthetic/{name}")
                  for name in _FIXED_ROOT_NAMES},
        "tool_dependency_roots": [], "python_dependency_roots": [],
    }, sort_keys=True, separators=(",", ":")).encode()
    malformed_s1 = FrozenArtifact("S1", "S1.json", malformed,
                                  hashlib.sha256(malformed).hexdigest(), len(malformed))
    with pytest.raises(EvidenceDagError) as escaped:
        s8_mod._expected_policy(malformed_s1)
    assert escaped.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE

    lineage = harness["build"](
        name="array-order", ordinal=30,
        observed_payload=_policy_dict(**{_READ_ONLY_KEY: permuted}),
    )
    with pytest.raises(EvidenceDagError) as end_to_end:
        s8_mod.capture_and_evaluate_s8(lineage["application"], lineage["s1"], lineage["seal"])
    assert end_to_end.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    assert len(harness["leaf_calls"]) == 1


@pytest.mark.parametrize("forbidden_key", [
    "com.apple.security.network.client",
    "com.apple.security.network.server",
    "com.apple.security.networking.networkextension",
    "com.apple.developer.networking.networkextension",
])
def test_each_prohibited_network_entitlement_fails(harness, forbidden_key):
    prohibited = (
        "com.apple.security.network.client",
        "com.apple.security.network.server",
        "com.apple.security.networking.networkextension",
        "com.apple.developer.networking.networkextension",
        "com.apple.security.temporary-exception.network.client",
        "com.apple.security.temporary-exception.network.server",
    )
    assert forbidden_key in prohibited[:4]
    additional_keys = {
        prohibited[0]: (prohibited[4],),
        prohibited[1]: (prohibited[5],),
        prohibited[2]: (),
        prohibited[3]: (),
    }
    for key in (forbidden_key, *additional_keys[forbidden_key]):
        for present_value in (True, False, 0, ""):
            with pytest.raises(EvidenceDagError) as violation:
                s8_mod._parse_payload(_policy_dict(**{key: present_value}))
            assert violation.value.code is EvidenceFailureCode.ENTITLEMENT_ALLOWLIST_VIOLATION

    payload = _policy_dict(**{forbidden_key: True})
    lineage = harness["build"](
        name=f"prohibited-{forbidden_key}", ordinal=31, observed_payload=payload,
    )
    with pytest.raises(EvidenceDagError) as end_to_end:
        s8_mod.capture_and_evaluate_s8(lineage["application"], lineage["s1"], lineage["seal"])
    assert end_to_end.value.code is EvidenceFailureCode.ENTITLEMENT_ALLOWLIST_VIOLATION
    assert len(harness["leaf_calls"]) == 1


def test_n5_positive_exact_bytes(harness, monkeypatch):
    mutation = harness["build"](name="mutation", ordinal=19, observed_payload=_policy_payload())
    original = mutation["application"]
    forged_cases = (
        object(),
        mutation["s1"],
        dataclasses.replace(original, _generation_identity="0" * 40),
        dataclasses.replace(original, _subject_path=Path("/tmp/elsewhere/StageBSandboxRunner.app")),
        dataclasses.replace(original, _subject_path=Path(mutation["seal"].commit_sha)),
        copy.copy(original),
        copy.deepcopy(original),
        type(original)(original._generation_identity, original._subject_path,
                       original._repository_context_token, original._lifecycle_token,
                       original._registration_token),
        dataclasses.replace(original, _lifecycle_token=object()),
    )
    for forged in forged_cases:
        with pytest.raises(EvidenceDagError) as forged_error:
            s8_mod.extract_s8_from_n4a_application(forged)
        assert forged_error.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
    assert not harness["leaf_calls"]

    payload = _policy_payload()
    lineage = harness["build"](name="positive", ordinal=20, observed_payload=payload)
    captured = s8_mod.capture_and_evaluate_s8(lineage["application"], lineage["s1"], lineage["seal"])
    assert type(captured) is S8Capture
    assert captured.exact_bytes == payload
    assert captured.sha256 == hashlib.sha256(payload).hexdigest()
    assert captured.parsed_policy == _expected_policy_for()
    assert len(harness["leaf_calls"]) == 1
    assert s8_mod._N5_STATE[id(lineage["application"])][2] == "CONSUMED"

    # A second caller must observe the atomic in-flight reservation before it can reach the leaf.
    concurrent = harness["build"](name="concurrent", ordinal=21, observed_payload=payload)
    entered = threading.Event()
    release = threading.Event()
    outcomes = []

    def blocking_leaf(application):
        harness["leaf_calls"].append(application)
        entered.set()
        assert release.wait(5)
        return subprocess.CompletedProcess(("synthetic-codesign",), 0, payload, b"")

    monkeypatch.setattr(s8_mod, "_run_codesign_entitlements", blocking_leaf)
    worker = threading.Thread(target=lambda: outcomes.append(
        s8_mod.extract_s8_from_n4a_application(concurrent["application"])))
    worker.start()
    assert entered.wait(5)
    with pytest.raises(EvidenceDagError) as in_flight:
        s8_mod.extract_s8_from_n4a_application(concurrent["application"])
    assert in_flight.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
    assert "in flight" in in_flight.value.reason
    assert len(harness["leaf_calls"]) == 1
    release.set()
    worker.join(5)
    assert not worker.is_alive()
    assert outcomes == [payload]

    # Distinct app/S1/seal generations cannot be spliced together; refusal is pre-leaf.
    generation_a = harness["build"](name="generation-a", ordinal=22, observed_payload=payload)
    generation_b = harness["build"](name="generation-b", ordinal=23, observed_payload=payload)
    harness["leaf_calls"].clear()
    with pytest.raises(EvidenceDagError) as cross_seal:
        s8_mod.capture_and_evaluate_s8(generation_a["application"], generation_b["s1"], generation_b["seal"])
    assert cross_seal.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
    assert "S7 parent" in cross_seal.value.reason
    assert not harness["leaf_calls"]
    assert id(generation_a["application"]) not in s8_mod._N5_STATE

    # A foreign S1 with different root evidence fails anchoring before N5 reservation.
    foreign_s1 = harness["build"](name="foreign-s1", ordinal=24, observed_payload=payload,
                                  roots=_ALT_ROOTS)
    harness["holder"]["root"] = generation_a["root"]
    harness["leaf_calls"].clear()
    with pytest.raises(EvidenceDagError) as cross_s1:
        s8_mod.capture_and_evaluate_s8(generation_a["application"], foreign_s1["s1"], generation_a["seal"])
    assert cross_s1.value.code is EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
    assert "anchored" in cross_s1.value.reason
    assert not harness["leaf_calls"]
    assert id(generation_a["application"]) not in s8_mod._N5_STATE

    # Pre-leaf refusals leave the registered application available for a valid capture.
    recovered = s8_mod.capture_and_evaluate_s8(
        generation_a["application"], generation_a["s1"], generation_a["seal"])
    assert recovered.exact_bytes == payload
    assert len(harness["leaf_calls"]) == 1

    # Invalidation during the leaf returns the reservation to the reusable state table.
    invalidated = harness["build"](name="invalidated", ordinal=25, observed_payload=payload)
    original_leaf = harness["leaf"]

    def invalidate_during_observation(application):
        result = original_leaf(application)
        boundary_mod._request_capture_invalidation(application, "synthetic invalidation")
        return result

    monkeypatch.setattr(s8_mod, "_run_codesign_entitlements", invalidate_during_observation)
    with pytest.raises(EvidenceDagError) as invalidation:
        s8_mod.extract_s8_from_n4a_application(invalidated["application"])
    assert invalidation.value.code is EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
    assert "NOT_OBSERVED:" in invalidation.value.reason
    assert id(invalidated["application"]) not in s8_mod._N5_STATE

    # Restore the lawful observation leaf before building later accepted lineages.
    monkeypatch.setattr(s8_mod, "_run_codesign_entitlements", original_leaf)

    # Both retained-payload failure classes must be reached after valid N4A lineage creation.
    mismatched_retention = harness["build"](
        name="mismatched-retention", ordinal=26, observed_payload=payload,
        embedded_payload=_policy_payload(_expected_policy_for(_ALT_ROOTS)),
    )
    with pytest.raises(EvidenceDagError) as parity:
        s8_mod.capture_and_evaluate_s8(
            mismatched_retention["application"], mismatched_retention["s1"], mismatched_retention["seal"])
    assert parity.value.code is EvidenceFailureCode.S8_NOT_RETAINED_EXACTLY
    assert len(harness["leaf_calls"]) == 1

    malformed_retention = harness["build"](
        name="malformed-retention", ordinal=27, observed_payload=payload,
        embedded_payload=b"\xffnot-plist\x00")
    with pytest.raises(EvidenceDagError) as malformed_parity:
        s8_mod.capture_and_evaluate_s8(
            malformed_retention["application"], malformed_retention["s1"], malformed_retention["seal"])
    assert malformed_parity.value.code is EvidenceFailureCode.S8_NOT_RETAINED_EXACTLY
    assert malformed_parity.value.reason.startswith("NOT_OBSERVED:")
    assert len(harness["leaf_calls"]) == 1
