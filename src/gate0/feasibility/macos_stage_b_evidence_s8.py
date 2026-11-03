"""Verifier-owned N5 S8 extraction for Gate 0 (WP-10)."""
from __future__ import annotations

import hashlib
import plistlib
import subprocess
import threading
from pathlib import Path

from gate0.feasibility import macos_stage_b_evidence_boundary as _boundary
from gate0.feasibility import macos_stage_b_evidence_git as _git
from gate0.feasibility import macos_stage_b_evidence_seal as _seal
from gate0.feasibility import macos_stage_b_evidence_snapshot as _snapshot
from gate0.feasibility.macos_stage_b_evidence_constants import (
    EvidenceDagError, EvidenceFailureCode, FrozenArtifact, N4ATransientApplication,
    ParsedEntitlementPolicy, S8Capture, SealResult, VerifiedRepositoryContext,
)

_READ_ONLY_KEY = "com.apple.security.temporary-exception.files.absolute-path.read-only"
_READ_WRITE_KEY = "com.apple.security.temporary-exception.files.absolute-path.read-write"
_PERMITTED_ENTITLEMENT_KEYS = frozenset({"com.apple.security.app-sandbox", _READ_ONLY_KEY, _READ_WRITE_KEY})
_PROHIBITED_ENTITLEMENT_KEYS = frozenset({
    "com.apple.security.network.client", "com.apple.security.network.server",
    "com.apple.security.networking.networkextension", "com.apple.developer.networking.networkextension",
    "com.apple.security.temporary-exception.network.client", "com.apple.security.temporary-exception.network.server",
})
_PROJECTION_MEMBER_PATHS = tuple(f"S9/{filename}" for _, filename, _ in _seal._MEMBER_FIELDS)
_N5_LOCK = threading.Lock()
_N5_STATE: dict[int, tuple[object, str, str, object]] = {}
_SIGNED_NOT_VERIFIER = EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
_ALLOWLIST = EvidenceFailureCode.ENTITLEMENT_ALLOWLIST_VIOLATION
_CLOSURE = EvidenceFailureCode.ENTITLEMENT_POLICY_CLOSURE_DIVERGENCE
_NOT_RETAINED = EvidenceFailureCode.S8_NOT_RETAINED_EXACTLY


def _fail(code, reason):
    raise EvidenceDagError(code, reason)


def extract_s8_from_n4a_application(application: N4ATransientApplication) -> bytes:
    if type(application) is not N4ATransientApplication:
        _fail(_SIGNED_NOT_VERIFIER, "transient application is not the exact verifier-owned type")
    with _boundary._REGISTRY_LOCK:
        record = _boundary._REGISTRY.get(id(application))
        record = None if record is None else tuple(record)
    if record is None or len(record) != 8 or record[0] is not application:
        _fail(_SIGNED_NOT_VERIFIER, "transient application is not the exact registered instance")
    context = record[1]
    if type(context) is not VerifiedRepositoryContext:
        _fail(_SIGNED_NOT_VERIFIER, "registered context is not the exact verifier-owned type")
    try:
        _boundary._validate_registered_handle(application, context)
    except EvidenceDagError:
        raise
    _record, _context, binding = _resolve_registered_context(application)

    expected_subject = (Path(context.canonical_root) / ".stage-b-build"
                        / context.generation_identity / "StageBSandboxRunner.app")
    token = _claim_n5_subject(application, str(application._subject_path))
    try:
        if application._subject_path != expected_subject:
            _fail(_SIGNED_NOT_VERIFIER, "transient application subject path diverges from its registered context")
        try:
            result = _run_codesign_entitlements(application)
        except Exception as error:
            _fail(_SIGNED_NOT_VERIFIER, f"NOT_OBSERVED: codesign entitlement observation raised {type(error).__name__}")
        if (type(result) is not subprocess.CompletedProcess or result.returncode != 0
                or type(result.stdout) is not bytes or not result.stdout):
            _fail(_SIGNED_NOT_VERIFIER, "NOT_OBSERVED: codesign entitlement observation was unavailable")
        _validate_after_observation(application, context, binding)
        _finish_n5_claim(token)
        return result.stdout
    except Exception:
        _release_n5_claim(token)
        raise


def capture_and_evaluate_s8(application: N4ATransientApplication, exact_s1: FrozenArtifact, seal: SealResult) -> S8Capture:
    """Capture S8 with same-generation and content-parity checks only.

    R-11 remains: this interface cannot prove exact N4a handoff identity.
    R-12 remains: the renderer's own exception taxonomy is not total.
    """
    record, context, binding = _resolve_registered_context(application)
    if (type(context) is not VerifiedRepositoryContext or record[1] is not context
            or binding.context is not context or binding.generation != context.generation_identity):
        _fail(_SIGNED_NOT_VERIFIER, "registered application context is inconsistent")
    if (type(exact_s1) is not FrozenArtifact or exact_s1.role != "S1"
            or exact_s1.repository_path != "S1.json" or type(exact_s1.data) is not bytes
            or exact_s1.sha256 != hashlib.sha256(exact_s1.data).hexdigest()
            or exact_s1.octets != len(exact_s1.data)):
        _fail(_SIGNED_NOT_VERIFIER, "S1 argument is not the exact frozen artifact")

    if (type(seal) is not SealResult
            or any(type(value) is not str or _git._HEX40.fullmatch(value) is None
                   for value in (seal.commit_sha, seal.tree_sha, seal.parent_s7_commit_sha))
            or seal.projection_members != _PROJECTION_MEMBER_PATHS):
        _fail(_SIGNED_NOT_VERIFIER, "seal fields are not the exact frozen projection shape")
    try:
        parent = _git.commit_parent(seal.commit_sha)
        tree = _git.commit_tree(seal.commit_sha)
    except EvidenceDagError:
        _fail(_SIGNED_NOT_VERIFIER, "seal commit cannot be re-read from Git")
    if parent != seal.parent_s7_commit_sha or tree != seal.tree_sha:
        _fail(_SIGNED_NOT_VERIFIER, "seal commit parent or tree diverges from its recorded fields")
    try:
        identity = _git.read_blob_at(seal.commit_sha, "S9/identity.json")
    except EvidenceDagError:
        _fail(_SIGNED_NOT_VERIFIER, "seal identity cannot be re-read from Git")
    if hashlib.sha256(identity).hexdigest() != seal.identity_json_sha256:
        _fail(_SIGNED_NOT_VERIFIER, "seal identity digest diverges from its committed bytes")
    if seal.parent_s7_commit_sha != context.evaluation_commit:
        _fail(_SIGNED_NOT_VERIFIER, "seal S7 parent is not the registered application's evaluation commit")
    try:
        anchored_s1 = _git.read_blob_at(context.evaluation_commit, "S1.json")
    except EvidenceDagError:
        _fail(_CLOSURE, "policy is not anchored to the exact S1")
    if anchored_s1 != exact_s1.data:
        _fail(_CLOSURE, "policy is not anchored to the exact S1")

    try:
        retained = _git.read_blob_at(seal.commit_sha, "S9/Entitlements.blob")
        retained_again = _git.read_blob_at(seal.commit_sha, "S9/Entitlements.blob")
    except EvidenceDagError:
        _fail(_NOT_RETAINED, "NOT_OBSERVED: retained entitlements payload is unavailable")
    if (retained != retained_again or len(retained) < 8
            or int.from_bytes(retained[:4], "big") != 0xFADE7171
            or int.from_bytes(retained[4:8], "big") != len(retained)):
        _fail(_NOT_RETAINED, "NOT_OBSERVED: retained entitlements payload is unavailable")

    expected = _expected_policy(exact_s1)
    exact_bytes = extract_s8_from_n4a_application(application)
    observed = _parse_payload(exact_bytes)
    _require_closure(observed, expected)
    retained_policy = _parse_retained(retained[8:])
    if (retained_policy.app_sandbox, retained_policy.read_only_paths,
            retained_policy.read_write_paths, retained_policy.keys) != (
            observed.app_sandbox, observed.read_only_paths, observed.read_write_paths, observed.keys):
        _fail(_NOT_RETAINED, "retained entitlements payload does not match the observed S8 bytes")
    return S8Capture(exact_bytes, hashlib.sha256(exact_bytes).hexdigest(), observed)


def _run_codesign_entitlements(application: N4ATransientApplication) -> subprocess.CompletedProcess[bytes]:
    if type(application) is not N4ATransientApplication:
        _fail(_SIGNED_NOT_VERIFIER, "transient application is not the exact verifier-owned type")
    argv = ("/usr/bin/codesign", "-d", "--entitlements", ":-", str(application._subject_path))
    return subprocess.run(
        argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False, shell=False, timeout=None, env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
    )


def _claim_n5_subject(application: N4ATransientApplication, subject_path: str) -> object:
    token = object()
    key = id(application)
    with _N5_LOCK:
        prior = _N5_STATE.get(key)
        if prior is not None:
            reason = "N5 subject is in flight" if prior[2] == "IN_FLIGHT" else "N5 subject was already consumed"
            _fail(_SIGNED_NOT_VERIFIER, reason)
        _N5_STATE[key] = (application, subject_path, "IN_FLIGHT", token)
    return token


def _finish_n5_claim(token: object) -> None:
    with _N5_LOCK:
        for key, record in _N5_STATE.items():
            if record[3] is token:
                if record[2] != "IN_FLIGHT":
                    _fail(_SIGNED_NOT_VERIFIER, "N5 reservation is not in flight")
                _N5_STATE[key] = (record[0], record[1], "CONSUMED", token)
                return
    _fail(_SIGNED_NOT_VERIFIER, "N5 reservation token is unknown")


def _release_n5_claim(token: object) -> None:
    with _N5_LOCK:
        for key, record in tuple(_N5_STATE.items()):
            if record[3] is token and record[2] == "IN_FLIGHT":
                del _N5_STATE[key]
                return


def _resolve_registered_context(application: N4ATransientApplication):
    if type(application) is not N4ATransientApplication:
        _fail(_SIGNED_NOT_VERIFIER, "transient application is not the exact verifier-owned type")
    with _boundary._REGISTRY_LOCK:
        record = _boundary._REGISTRY.get(id(application))
    if record is None or len(record) != 8 or record[0] is not application:
        _fail(_SIGNED_NOT_VERIFIER, "transient application is not the exact registered instance")
    context = record[1]
    if type(context) is not VerifiedRepositoryContext:
        _fail(_SIGNED_NOT_VERIFIER, "registered context is not the exact verifier-owned type")
    with _boundary._SOURCE_LIFECYCLE_LOCK:
        binding = _boundary._CAPTURE_BINDINGS.get(id(application))
        exact_binding = binding is not None and binding.application is application
        if exact_binding:
            binding_state = binding.state
            binding_context = binding.context
            binding_generation = binding.generation
        else:
            binding_state = None
            binding_context = None
            binding_generation = None
    if (not exact_binding or binding_context is not context
            or binding_generation != context.generation_identity or binding_state != "ACCEPTED"):
        _fail(_SIGNED_NOT_VERIFIER, "transient application has no accepted exact capture binding")
    return record, context, binding


def _validate_after_observation(application, context, binding) -> None:
    try:
        _boundary._validate_registered_handle(application, context)
    except EvidenceDagError:
        _fail(_SIGNED_NOT_VERIFIER, "NOT_OBSERVED: application registration changed during entitlement observation")
    with _boundary._SOURCE_LIFECYCLE_LOCK:
        exact = (_boundary._CAPTURE_BINDINGS.get(id(application)) is binding
                 and binding.application is application and binding.context is context
                 and binding.generation == context.generation_identity and binding.state == "ACCEPTED")
    if not exact:
        _fail(_SIGNED_NOT_VERIFIER, "NOT_OBSERVED: capture binding changed during entitlement observation")


def _expected_policy(exact_s1: FrozenArtifact) -> ParsedEntitlementPolicy:
    try:
        rendered = _snapshot.render_s2_from_s1(exact_s1)
    except EvidenceDagError as error:
        if error.code is EvidenceFailureCode.RENDER_INPUT_NOT_FROZEN:
            raise
        _fail(_CLOSURE, f"expected-policy renderer raised {type(error).__name__}")
    except Exception as error:
        _fail(_CLOSURE, f"expected-policy renderer raised {type(error).__name__}")
    if (type(rendered) is not FrozenArtifact or rendered.role != "S2"
            or rendered.repository_path != "S2.plist" or type(rendered.data) is not bytes
            or rendered.sha256 != hashlib.sha256(rendered.data).hexdigest()
            or rendered.octets != len(rendered.data)):
        _fail(_CLOSURE, "expected-policy renderer did not return the exact S2 artifact")
    try:
        return _parse_payload(rendered.data)
    except EvidenceDagError as error:
        if error.code is _ALLOWLIST:
            raise
        _fail(_CLOSURE, "expected policy is not renderable")


def _parse_payload(stdout: bytes) -> ParsedEntitlementPolicy:
    if type(stdout) is not bytes:
        _fail(_CLOSURE, "entitlement payload is not bytes")
    try:
        root = plistlib.loads(stdout)
    except Exception as error:
        _fail(_CLOSURE, f"entitlement payload is not a renderable plist: {type(error).__name__}")
    if type(root) is not dict:
        _fail(_CLOSURE, "entitlement payload root is not a dictionary")
    keys = set(root)
    if keys - _PERMITTED_ENTITLEMENT_KEYS:
        _fail(_ALLOWLIST, "entitlement payload declares a prohibited or unapproved key")
    sandbox = root.get("com.apple.security.app-sandbox")
    if type(sandbox) is not bool or sandbox is not True:
        _fail(_CLOSURE, "app-sandbox is not the singleton True")
    if keys != _PERMITTED_ENTITLEMENT_KEYS:
        _fail(_CLOSURE, "entitlement key set is not the exact permitted set")
    paths = {}
    for key in (_READ_ONLY_KEY, _READ_WRITE_KEY):
        value = root[key]
        if type(value) is not list or any(type(element) is not str for element in value):
            _fail(_CLOSURE, f"{key} is not a list of strings")
        paths[key] = tuple(value)
    return ParsedEntitlementPolicy(True, paths[_READ_ONLY_KEY], paths[_READ_WRITE_KEY], tuple(sorted(keys)))


def _parse_retained(payload: bytes) -> ParsedEntitlementPolicy:
    try:
        return _parse_payload(payload)
    except EvidenceDagError:
        _fail(_NOT_RETAINED, "NOT_OBSERVED: retained entitlements payload is not parseable")


def _require_closure(observed: ParsedEntitlementPolicy, expected: ParsedEntitlementPolicy) -> None:
    if type(observed) is not ParsedEntitlementPolicy or type(expected) is not ParsedEntitlementPolicy:
        _fail(_CLOSURE, "entitlement policy is not the exact parsed type")
    if observed.keys != expected.keys:
        _fail(_CLOSURE, "entitlement key sets diverge")
    if type(observed.app_sandbox) is not bool or observed.app_sandbox is not True:
        _fail(_CLOSURE, "observed app-sandbox value diverges")
    if type(expected.app_sandbox) is not bool or expected.app_sandbox is not True:
        _fail(_CLOSURE, "expected app-sandbox value is not the singleton True")
    if observed.read_only_paths != expected.read_only_paths:
        _fail(_CLOSURE, "read-only path list diverges from the renderer-derived policy")
    if observed.read_write_paths != expected.read_write_paths:
        _fail(_CLOSURE, "read-write path list diverges from the renderer-derived policy")
