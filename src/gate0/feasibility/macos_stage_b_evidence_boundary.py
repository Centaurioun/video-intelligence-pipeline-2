"""Verifier-owned N4a build boundary for Gate-0 Revision-18.

The public input surface accepts only S7-registered, exact-instance evidence and
never accepts an expectation, destination selector, or signing seed.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import threading
import weakref
from dataclasses import dataclass

from gate0.feasibility import macos_stage_b_evidence_anchor as anchor_mod
from gate0.feasibility import macos_stage_b_evidence_git as git_mod
from gate0.feasibility import macos_stage_b_evidence_snapshot as snapshot_mod
from gate0.feasibility.macos_stage_b_evidence_constants import (
    AnchoredS1Handle, EvidenceDagError, EvidenceFailureCode, FrozenArtifact,
    N4ABoundaryPrimitive, N4AProductionResult, N4ASealCapability, N4ASealHandoff,
    N4ATransientApplication, S7AnchorCreateResult, VerifierOwnedBuildContext,
    VerifierOwnedSealedDestination, VerifierOwnedSigningIdentity,
    VerifiedRepositoryContext,
)

_FAILURE = EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
BUILD_ENVIRONMENT_KEYS = frozenset({
    "GATE0_STAGE_B_FROZEN_S2", "GATE0_STAGE_B_SEALED_DESTINATION", "STAGE_B_SIGN_IDENTITY", "HOME",
    "TMPDIR", "XDG_CACHE_HOME", "PATH",
})
_REGISTRY: dict[int, tuple[
    object, VerifiedRepositoryContext, str, str, bool,
    N4ABoundaryPrimitive | None,
    tuple[weakref.ReferenceType[N4ASealHandoff], object] | bool | None,
    object | None,
]] = {}
_REGISTRY_LOCK = threading.Lock()
_TOKEN = object()
_SOURCE_LIFECYCLE_LOCK = threading.Lock()
_CAPTURE_BINDINGS: dict[int, "_CaptureBinding"] = {}


@dataclass
class _CaptureBinding:
    application: N4ATransientApplication
    context: VerifiedRepositoryContext
    generation: str
    invocation_token: object
    registration_token: object
    state: str = "ACQUIRING"
    eligibility_version: int = 0
    refusal_reason: str | None = None
    session: object | None = None


def _fail(reason: str) -> EvidenceDagError:
    return EvidenceDagError(_FAILURE, reason)


def _registered_application_record(application, context) -> bool:
    with _REGISTRY_LOCK:
        record = _REGISTRY.get(id(application))
    return bool(
        record is not None and len(record) == 8 and record[0] is application
        and record[1] is context and record[2] == context.generation_identity
        and record[3] == "transient-app" and record[4] is False
        and application._generation_identity == record[2]
        and application._repository_context_token is context._registration_token
    )


def _establish_capture_binding(application, context, build_context) -> None:
    """Bind the exact registered application to its origin graph before return."""
    if (type(application) is not N4ATransientApplication
            or type(context) is not VerifiedRepositoryContext
            or build_context.repository_context is not context
            or not _registered_application_record(application, context)):
        raise _fail("capture registration does not match exact live application and context")
    binding = _CaptureBinding(
        application=application,
        context=context,
        generation=context.generation_identity,
        invocation_token=application._lifecycle_token,
        registration_token=application._registration_token,
    )
    with _SOURCE_LIFECYCLE_LOCK:
        if id(application) in _CAPTURE_BINDINGS:
            raise _fail("capture binding already exists for this application")
        _CAPTURE_BINDINGS[id(application)] = binding
    try:
        from gate0.feasibility import macos_stage_b_evidence_projection as projection
        session = projection._acquire_origin_graph(context, application)
    except EvidenceDagError as exc:
        with _SOURCE_LIFECYCLE_LOCK:
            binding.state = "REFUSED"
            binding.refusal_reason = str(exc)
            binding.eligibility_version += 1
        return
    with _SOURCE_LIFECYCLE_LOCK:
        if _CAPTURE_BINDINGS.get(id(application)) is binding:
            binding.session = session
    if session.refusal_reason is not None or not session.origin_live:
        with _SOURCE_LIFECYCLE_LOCK:
            binding.session = session
            binding.state = "REFUSED"
            binding.refusal_reason = session.refusal_reason or "NOT_OBSERVED: origin graph acquisition failed"
            binding.eligibility_version += 1
        return
    if not _registered_application_record(application, context):
        from gate0.feasibility import macos_stage_b_evidence_projection as projection
        projection._release_origin_graph(session)
        with _SOURCE_LIFECYCLE_LOCK:
            binding.state = "REFUSED"
            binding.refusal_reason = "NOT_OBSERVED: application registration changed during graph acquisition"
            binding.eligibility_version += 1
        return
    with _SOURCE_LIFECYCLE_LOCK:
        keep_session = binding.state == "ACQUIRING"
        if keep_session:
            binding.session = session
            binding.state = "ELIGIBLE"
            binding.eligibility_version += 1
        else:
            binding.refusal_reason = binding.refusal_reason or "capture eligibility was lost during registration"
    if not keep_session:
        from gate0.feasibility import macos_stage_b_evidence_projection as projection
        projection._release_origin_graph(session)


def _capture_eligibility(binding) -> bool:
    if type(binding) is not _CaptureBinding:
        return False
    with _SOURCE_LIFECYCLE_LOCK:
        exact = _CAPTURE_BINDINGS.get(id(binding.application)) is binding
        eligible = binding.state == "ELIGIBLE" and binding.session is not None
    return exact and eligible and _registered_application_record(binding.application, binding.context)


def _begin_capture(application) -> _CaptureBinding:
    with _SOURCE_LIFECYCLE_LOCK:
        binding = _CAPTURE_BINDINGS.get(id(application))
        exact = binding is not None and binding.application is application
        eligible = exact and binding.state == "ELIGIBLE" and binding.session is not None
    if (not eligible or type(application) is not N4ATransientApplication
            or application._lifecycle_token is not binding.invocation_token
            or application._registration_token is not binding.registration_token
            or not _registered_application_record(application, binding.context)):
        raise _fail("NOT_OBSERVED: application has no live capture-eligible origin binding")
    with _SOURCE_LIFECYCLE_LOCK:
        if (_CAPTURE_BINDINGS.get(id(application)) is not binding
                or binding.state != "ELIGIBLE"):
            raise _fail("NOT_OBSERVED: application capture lifecycle changed")
        binding.state = "CAPTURING"
        binding.eligibility_version += 1
    return binding


def _publish_capture(binding, fields: dict[str, object]):
    from gate0.feasibility.macos_stage_b_evidence_constants import VerifiedSignedImageProjectionSource
    if (type(binding) is not _CaptureBinding
            or not _registered_application_record(binding.application, binding.context)):
        raise _fail("NOT_OBSERVED: capture eligibility was lost before source publication")
    source = VerifiedSignedImageProjectionSource(
        source_application=binding.application,
        generation_identity=binding.generation,
        repository_context=binding.context,
        executable_code_region_bytes=fields["executable_code_region_bytes"],
        info_plist_bytes=fields["info_plist_bytes"],
        code_resources_bytes=fields["code_resources_bytes"],
        superblob_index_bytes=fields["superblob_index_bytes"],
        code_directory_bytes=fields["code_directory_bytes"],
        entitlements_blob_bytes=fields["entitlements_blob_bytes"],
        der_entitlements_blob_bytes=fields["der_entitlements_blob_bytes"],
        requirements_blob_sha256=fields["requirements_blob_sha256"],
        cms_signature_blob_sha256=fields["cms_signature_blob_sha256"],
        special_slot_state=fields["special_slot_state"],
        code_directory_identity=fields["code_directory_identity"],
        _capture_registration=binding.registration_token,
    )
    with _SOURCE_LIFECYCLE_LOCK:
        if (_CAPTURE_BINDINGS.get(id(binding.application)) is not binding
                or binding.state != "CAPTURING"):
            raise _fail("NOT_OBSERVED: capture eligibility changed during source publication")
        binding.state = "ACCEPTED"
        binding.eligibility_version += 1
        binding.session.accepted = True
    return source


def _refuse_capture(binding, reason: str) -> None:
    if type(binding) is not _CaptureBinding:
        return
    with _SOURCE_LIFECYCLE_LOCK:
        if _CAPTURE_BINDINGS.get(id(binding.application)) is binding:
            binding.state = "REFUSED"
            binding.refusal_reason = reason
            binding.eligibility_version += 1


def _request_capture_invalidation(application, reason: str) -> None:
    with _SOURCE_LIFECYCLE_LOCK:
        binding = _CAPTURE_BINDINGS.get(id(application))
        if binding is None or binding.application is not application:
            return
        binding.state = "REFUSED"
        binding.refusal_reason = reason
        binding.eligibility_version += 1


def _register(handle: object, context: VerifiedRepositoryContext, generation: str,
              kind: str, used: bool = False,
              primitive: N4ABoundaryPrimitive | None = None,
              lifecycle_token: object | None = None) -> None:
    with _REGISTRY_LOCK:
        _REGISTRY[id(handle)] = (
            handle, context, generation, kind, used, primitive,
            None if kind == "seal-capability" else False, lifecycle_token,
        )


def _validate_registered_handle(
    handle: VerifierOwnedSealedDestination | VerifierOwnedSigningIdentity | VerifierOwnedBuildContext | N4ASealCapability | N4ATransientApplication,
    repository_context: VerifiedRepositoryContext,
) -> None:
    with _REGISTRY_LOCK:
        record = _REGISTRY.get(id(handle))
    if (record is None or record[0] is not handle or record[1] is not repository_context
            or record[2] != repository_context.generation_identity or record[4]):
        raise _fail("handle is not the exact current registered instance")
    if type(handle) is VerifierOwnedBuildContext:
        if (handle.repository_context is not repository_context or handle.generation_identity != record[2]
                or handle._registration_token is None):
            raise _fail("build context lineage mismatch")
        _validate_registered_handle(handle.sealed_destination, repository_context)
        _validate_registered_handle(handle.signing_identity, repository_context)
    elif type(handle) is VerifierOwnedSealedDestination:
        _validate_destination_identity(handle, repository_context)
    elif type(handle) is VerifierOwnedSigningIdentity:
        if (handle.generation_identity != repository_context.generation_identity
                or handle.repository_context_token is not repository_context._registration_token
                or not isinstance(handle.value, str) or not handle.value.startswith("s4-sha256:")):
            raise _fail("signing handle lineage mismatch")
    elif type(handle) is N4ASealCapability:
        if (handle._generation_identity != repository_context.generation_identity
                or handle._repository_context_token is not repository_context._registration_token
                or handle._lifecycle_token is not record[7]):
            raise _fail("seal capability lineage mismatch")
    elif type(handle) is N4ATransientApplication:
        expected_subject = (Path(repository_context.canonical_root) / ".stage-b-build"
                            / repository_context.generation_identity / "StageBSandboxRunner.app")
        if (handle._generation_identity != repository_context.generation_identity
                or handle._repository_context_token is not repository_context._registration_token
                or handle._subject_path != expected_subject):
            raise _fail("transient application lineage mismatch")
    else:
        raise _fail("unsupported registered handle type")


def _take_compatibility_primitive(record: tuple[object, ...]) -> N4ABoundaryPrimitive:
    primitive = record[5]
    if type(primitive) is not N4ABoundaryPrimitive:
        raise _fail("registered measured primitive has invalid type")
    return primitive


def _bind_n4a_handoff(
    capability: N4ASealCapability,
    handoff: N4ASealHandoff,
) -> None:
    if type(capability) is not N4ASealCapability or type(handoff) is not N4ASealHandoff:
        raise _fail("N4A handoff binding requires exact capability and handoff types")
    with _REGISTRY_LOCK:
        record = _REGISTRY.get(id(capability))
        source_record = _REGISTRY.get(id(handoff.source_application))
        if (record is None or len(record) != 8 or record[0] is not capability
                or record[3] != "seal-capability" or record[4] is not False
                or capability._generation_identity != record[2]
                or capability._repository_context_token is not record[1]._registration_token
                or capability._lifecycle_token is not record[7]
                or record[7] is None or record[6] is not None
                or handoff.capability is not capability
                or handoff.measured_primitive is not record[5]
                or source_record is None or source_record[0] is not handoff.source_application
                or source_record[1] is not record[1] or source_record[2] != record[2]
                or source_record[3] != "transient-app" or source_record[4] is not False
                or handoff.source_application._generation_identity != record[2]
                or handoff.source_application._repository_context_token
                is not record[1]._registration_token):
            raise _fail("handoff is not the exact live capability-bound value")
        _REGISTRY[id(capability)] = (
            *record[:6], (weakref.ref(handoff), record[7]), record[7],
        )


def _claim_n4a_lifecycle(
    capability: N4ASealCapability,
    repository_context: VerifiedRepositoryContext,
    *,
    claimant: str,
    handoff: N4ASealHandoff | None = None,
) -> N4ABoundaryPrimitive | None:
    if type(capability) is not N4ASealCapability:
        raise _fail("primitive capability must be the exact opaque instance")
    if (claimant == "legacy_consume" and handoff is not None) or (
        claimant == "n4b_seal" and type(handoff) is not N4ASealHandoff
    ) or claimant not in {"legacy_consume", "n4b_seal"}:
        raise _fail("N4A lifecycle claimant is invalid")
    with _REGISTRY_LOCK:
        record = _REGISTRY.get(id(capability))
        if (record is None or len(record) != 8 or record[0] is not capability
                or record[1] is not repository_context
                or record[2] != repository_context.generation_identity
                or record[3] != "seal-capability"
                or capability._generation_identity != record[2]
                or capability._repository_context_token
                is not repository_context._registration_token
                or capability._lifecycle_token is not record[7]
                or record[7] is None):
            raise _fail("N4A lifecycle capability is forged, stale, or cross-generation")
        if record[4] is not False:
            raise _fail("N4A lifecycle capability is already consumed")
        if claimant == "legacy_consume":
            primitive = _take_compatibility_primitive(record)
            _REGISTRY[id(capability)] = (
                *record[:4], True, None, record[6], record[7],
            )
            return primitive
        registration = record[6]
        if (type(registration) is not tuple or len(registration) != 2
                or not isinstance(registration[0], weakref.ReferenceType)
                or registration[1] is not record[7]):
            raise _fail("N4A handoff is not registered for this capability")
        registered_handoff = registration[0]()
        if registered_handoff is not handoff:
            raise _fail("N4A handoff is not the exact registered live instance")
        _REGISTRY[id(capability)] = (
            *record[:4], True, None, record[6], record[7],
        )
        return None


def _consume_n4a_primitive(
    capability: N4ASealCapability,
    repository_context: VerifiedRepositoryContext,
) -> N4ABoundaryPrimitive:
    """Consume the contemporaneous measured primitive for this exact capability once."""
    primitive = _claim_n4a_lifecycle(
        capability, repository_context, claimant="legacy_consume",
    )
    if type(primitive) is not N4ABoundaryPrimitive:
        raise _fail("registered measured primitive has invalid type")
    return primitive


def _validate_destination_identity(
    destination: VerifierOwnedSealedDestination,
    repository_context: VerifiedRepositoryContext,
) -> None:
    with _REGISTRY_LOCK:
        record = _REGISTRY.get(id(destination))
    if (type(destination) is not VerifierOwnedSealedDestination or record is None
            or record[0] is not destination or record[1] is not repository_context
            or record[2] != repository_context.generation_identity
            or destination.generation_identity != repository_context.generation_identity
            or destination.repository_context_token is not repository_context._registration_token):
        raise _fail("destination is not the exact context-bound handle")
    root = Path(repository_context.canonical_root) / ".stage-b-build" / destination.generation_identity
    if destination.scratch_root != root or destination.application_path != root / "StageBSandboxRunner.app":
        raise _fail("destination path differs from verifier-derived path")
    try:
        for component in (Path(repository_context.canonical_root) / ".stage-b-build",
                          destination.scratch_root, destination.scratch_root / "private"):
            st_component = component.lstat()
            if component.is_symlink() or not component.is_dir() or st_component.st_nlink < 1:
                raise _fail("destination ancestor was replaced")
        st = Path(repository_context.canonical_root).stat(follow_symlinks=False)
        if st.st_dev != repository_context.root_device or st.st_ino != repository_context.root_inode:
            raise _fail("repository root identity changed")
        if destination.application_path.exists() or destination.application_path.is_symlink():
            raise _fail("destination is not absent before build")
    except OSError as exc:
        raise _fail(f"destination identity check failed: {type(exc).__name__}") from exc


def _create_verifier_owned_build_context(
    repository_context: VerifiedRepositoryContext,
    anchor: S7AnchorCreateResult,
) -> VerifierOwnedBuildContext:
    git_mod._validate_verified_repository_context(repository_context)
    if type(anchor) is not S7AnchorCreateResult or anchor.commit_sha != repository_context.evaluation_commit:
        raise _fail("S7 anchor is not the exact evaluation commit")
    if not anchor_mod.verify_s7_anchor(anchor, tuple(
        FrozenArtifact(role, path, raw, hashlib.sha256(raw).hexdigest(), len(raw))
        for role, path in (("S1", "S1.json"), ("S2", "S2.plist"), ("S3", "S3.json"), ("S4", "S4.json"))
        for raw in (git_mod.read_blob_at(anchor.commit_sha, path),)
    )).passed:
        raise _fail("S7 anchor did not verify")
    s4 = git_mod.read_blob_at(anchor.commit_sha, "S4.json")
    # The signing selector is derived only from anchored S4 bytes; no caller
    # supplies or retains a raw certificate/private-key seed.
    signing_value = "s4-sha256:" + hashlib.sha256(s4).hexdigest()
    scratch = Path(repository_context.canonical_root) / ".stage-b-build" / repository_context.generation_identity
    private = scratch / "private"
    destination_path = scratch / "StageBSandboxRunner.app"
    try:
        build_parent = Path(repository_context.canonical_root) / ".stage-b-build"
        if build_parent.exists() or build_parent.is_symlink():
            raise _fail("build parent already exists or is a symlink")
        build_parent.mkdir(mode=0o700)
        scratch.mkdir(mode=0o700)
        private.mkdir(mode=0o700)
        for component in (build_parent, scratch, private):
            st = component.lstat()
            if component.is_symlink() or not component.is_dir() or st.st_nlink < 1:
                raise _fail("build path component was replaced")
    except OSError as exc:
        raise _fail(f"cannot establish exclusive build root: {type(exc).__name__}") from exc
    destination = VerifierOwnedSealedDestination(scratch, destination_path,
        repository_context.generation_identity, repository_context._registration_token, object())
    identity = VerifierOwnedSigningIdentity(signing_value, repository_context.generation_identity,
        repository_context._registration_token, object())
    _register(destination, repository_context, repository_context.generation_identity, "destination")
    _register(identity, repository_context, repository_context.generation_identity, "identity")
    context = VerifierOwnedBuildContext(repository_context, destination, identity,
        repository_context.generation_identity, object())
    _register(context, repository_context, repository_context.generation_identity, "build-context")
    return context


def _write_private_s2(s2: FrozenArtifact, build_context: VerifierOwnedBuildContext) -> Path:
    ctx = build_context.repository_context
    _validate_registered_handle(build_context, ctx)
    if type(s2) is not FrozenArtifact or s2.role != "S2" or type(s2.data) is not bytes:
        raise _fail("private S2 must be exact immutable S2 bytes")
    if hashlib.sha256(s2.data).hexdigest() != s2.sha256 or len(s2.data) != s2.octets:
        raise _fail("private S2 digest or length mismatch")
    destination = build_context.sealed_destination
    path = destination.scratch_root / "private" / "S2.plist"
    try:
        parent = path.parent
        if parent.is_symlink() or not parent.is_dir():
            raise _fail("private S2 directory is not verifier-owned")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(s2.data)
            stream.flush()
            os.fsync(stream.fileno())
        st = path.lstat()
        if not path.is_file() or path.is_symlink() or st.st_nlink != 1 or path.read_bytes() != s2.data:
            raise _fail("private S2 readback differs")
        return path
    except EvidenceDagError:
        raise
    except OSError as exc:
        raise _fail(f"private S2 creation/readback failed: {type(exc).__name__}") from exc


def _run_stage_b_build_process(
    s2: FrozenArtifact,
    build_context: VerifierOwnedBuildContext,
    private_s2_file: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[bytes]:
    raise _fail("build process execution is deferred to its separately authorized task")


def invoke_stage_b_build_app(
    s2: FrozenArtifact,
    build_context: VerifierOwnedBuildContext,
) -> N4ATransientApplication:
    context = build_context.repository_context
    _validate_registered_handle(build_context, context)
    private_s2 = _write_private_s2(s2, build_context)
    root = build_context.sealed_destination.scratch_root
    env: dict[str, str] = {}
    env.update({
        "GATE0_STAGE_B_FROZEN_S2": str(private_s2),
        "GATE0_STAGE_B_SEALED_DESTINATION": str(build_context.sealed_destination.application_path),
        "STAGE_B_SIGN_IDENTITY": build_context.signing_identity.value,
        "HOME": str(root / "home"), "TMPDIR": str(root / "tmp"),
        "XDG_CACHE_HOME": str(root / "cache"), "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
    })
    if frozenset(env) != BUILD_ENVIRONMENT_KEYS:
        raise _fail("controlled build environment has unexpected keys")
    result = _run_stage_b_build_process(s2, build_context, private_s2, env)
    if result.returncode != 0:
        raise _fail("build process returned failure")
    subject = build_context.sealed_destination.application_path
    try:
        for component in (Path(context.canonical_root) / ".stage-b-build",
                          build_context.sealed_destination.scratch_root,
                          build_context.sealed_destination.scratch_root / "private"):
            component_stat = component.lstat()
            if component.is_symlink() or not component.is_dir() or component_stat.st_nlink < 1:
                raise _fail("completed destination ancestor was replaced")
        root_stat = Path(context.canonical_root).stat(follow_symlinks=False)
        app_stat = subject.lstat()
        if (root_stat.st_dev != context.root_device or root_stat.st_ino != context.root_inode
                or subject.is_symlink() or not subject.is_dir() or app_stat.st_nlink < 1):
            raise _fail("completed destination identity changed")
    except OSError as exc:
        raise _fail(f"completed destination could not be revalidated: {type(exc).__name__}") from exc
    with _REGISTRY_LOCK:
        for consumed in (build_context, build_context.sealed_destination, build_context.signing_identity):
            record = _REGISTRY.get(id(consumed))
            if record is not None and record[0] is consumed:
                _REGISTRY[id(consumed)] = (*record[:4], True)
    app = N4ATransientApplication(context.generation_identity, subject,
        context._registration_token, object(), object())
    _register(app, context, context.generation_identity, "transient-app")
    try:
        _establish_capture_binding(app, context, build_context)
    except BaseException as exc:
        _abandon_registered_application_capture(app, exc)
        raise
    return app


def _validate_n4a_lineage(anchored_s1: AnchoredS1Handle, anchored_s2: FrozenArtifact,
                          build_context: VerifierOwnedBuildContext) -> FrozenArtifact:
    context = build_context.repository_context
    for parent_handle, parent_kind in ((context, "repository-context"), (anchored_s1, "anchored-s1")):
        with _REGISTRY_LOCK:
            record = _REGISTRY.get(id(parent_handle))
            if record is None:
                _REGISTRY[id(parent_handle)] = (
                    parent_handle, context, context.generation_identity, parent_kind,
                    False, None, False, None,
                )
            elif (record[0] is not parent_handle or record[1] is not context
                  or record[2] != context.generation_identity or record[4]):
                raise _fail(f"{parent_kind} handle was forged, stale, or already consumed")
    git_mod._validate_verified_repository_context(context)
    _validate_registered_handle(build_context, context)
    s1 = anchor_mod._extract_registered_anchored_s1(anchored_s1, context)
    if type(anchored_s2) is not FrozenArtifact or anchored_s2.role != "S2":
        raise _fail("S2 is not the exact anchored role")
    produced = snapshot_mod.render_s2_from_s1(s1)
    if produced.data != anchored_s2.data or produced.sha256 != anchored_s2.sha256 or produced.octets != anchored_s2.octets:
        raise _fail("same renderer did not reproduce anchored S2")
    return produced


def _abandon_registered_application_capture(application, failure: BaseException) -> None:
    """Terminally refuse and release capture ownership after a failed N4A return."""
    with _SOURCE_LIFECYCLE_LOCK:
        binding = _CAPTURE_BINDINGS.get(id(application))
        if binding is None or binding.application is not application:
            return
        binding.state = "REFUSED"
        binding.refusal_reason = (
            f"NOT_OBSERVED: N4A production failed after application registration: "
            f"{type(failure).__name__}"
        )
        binding.eligibility_version += 1
        session = binding.session
    if session is None:
        return
    try:
        from gate0.feasibility import macos_stage_b_evidence_projection as projection
        projection._release_origin_graph(session)
    except BaseException as cleanup_failure:
        with _SOURCE_LIFECYCLE_LOCK:
            if _CAPTURE_BINDINGS.get(id(application)) is binding:
                binding.refusal_reason += (
                    f"; NOT_OBSERVED: capture cleanup remains unresolved: "
                    f"{type(cleanup_failure).__name__}"
                )


def measure_and_handoff_n4a(
    anchored_s1: AnchoredS1Handle,
    anchored_s2: FrozenArtifact,
    build_context: VerifierOwnedBuildContext,
) -> N4AProductionResult:
    produced_s2 = _validate_n4a_lineage(anchored_s1, anchored_s2, build_context)
    application = invoke_stage_b_build_app(produced_s2, build_context)
    try:
        from gate0.feasibility.macos_stage_b_evidence_s8 import _run_codesign_entitlements
        signed_observation = _run_codesign_entitlements(application)
        if (type(signed_observation) is not subprocess.CompletedProcess
                or signed_observation.returncode != 0 or type(signed_observation.stdout) is not bytes):
            raise _fail("signer entitlements observation is not immutable bytes")
        signer_entitlements = signed_observation.stdout
        s1 = anchor_mod._extract_registered_anchored_s1(anchored_s1, build_context.repository_context)
        primitive = N4ABoundaryPrimitive(
            "N4A_BOUNDARY_PRIMITIVE_V1", hashlib.sha256(s1.data).hexdigest(), len(s1.data),
            hashlib.sha256(signer_entitlements).hexdigest(), len(signer_entitlements),
        )
        capability = N4ASealCapability(build_context.generation_identity,
            build_context.repository_context._registration_token, object(), object())
        _register(capability, build_context.repository_context, build_context.generation_identity,
                  "seal-capability", primitive=primitive, lifecycle_token=capability._lifecycle_token)
        from gate0.feasibility import macos_stage_b_evidence_projection as projection
        captured_source = projection.capture_signed_image_projection_source(application)
        signed_projection = projection.project_signed_image(captured_source, primitive)
        handoff = N4ASealHandoff(primitive, capability, signed_projection, application)
        _bind_n4a_handoff(capability, handoff)
        result = N4AProductionResult(primitive, capability, application, produced_s2, handoff)
        with _REGISTRY_LOCK:
            for consumed in (build_context.repository_context, anchored_s1):
                record = _REGISTRY[id(consumed)]
                _REGISTRY[id(consumed)] = (*record[:4], True)
        return result
    except BaseException as exc:
        _abandon_registered_application_capture(application, exc)
        raise
