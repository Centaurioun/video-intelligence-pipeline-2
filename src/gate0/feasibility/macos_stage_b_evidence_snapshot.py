"""Verifier-owned canonical S1/S2/S3/S4 snapshot derivation for Revision-18."""
from __future__ import annotations

import hashlib
import json
import plistlib
import re
from pathlib import Path, PurePath, PurePosixPath
from typing import Iterable

from gate0.feasibility.macos_stage_b_evidence_authority import derive_generation_identity, validate_s4_echo
from gate0.feasibility.macos_stage_b_evidence_constants import (
    AuthorityTuple,
    CanonicalizationFailureReason,
    CanonicalizationResult,
    CensusNamespaceRow,
    CanonicalizationTerminalFamily,
    DependencyInventoryEntry,
    EntryKind,
    EvidenceDagError,
    EvidenceFailureCode,
    FrozenArtifact,
    FrozenSnapshotSet,
    CensusScopeTag,
    NativeManifestRow,
    ProducerSnapshotInputs,
    StableCensusResult,
    VerifierSnapshotInputs,
)
from gate0.feasibility.macos_stage_b_evidence_macho import MACHO_NATIVE_CONTAINER_PARSE_V1
from gate0.feasibility.macos_stage_b_evidence_runtime import serialize_native_manifest
from gate0.feasibility.macos_stage_b_v3_schema import EXECUTION_MODES

_FAILURE = EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID
_FIXED_ROOT_NAMES = (
    "worktree", "worktree_src", "python", "python_runtime", "model",
    "synthetic", "ffmpeg", "ffprobe", "output",
)
_SYSTEM_ROOTS = ("/usr/lib", "/System/Library")
_CELLAR_ROOT = "/opt/homebrew/Cellar"
_FFMPEG_SEED_SHA256 = "9f5ddd4f8b36eb07b0c5d60ab6ea1e618bedd70bc45feab82b4dc23be1596ad1"
_FFPROBE_SEED_SHA256 = "0ecd5e1affb1466b129b4f65bee261e9ab625c4d4a2e7c3e9089f63d44808605"
_PYTHON_SEED_SHA256 = "87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634"
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
# No owner-approved native closure baseline has been measured and pinned.
_OWNER_PINNED_NATIVE_PROFILE_V1: tuple[str, int] | None = None
_OPTIONAL_SEEDS_V1: tuple[()] = ()


def _fail(reason: str) -> EvidenceDagError:
    return EvidenceDagError(_FAILURE, reason)


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _artifact(role: str, repository_path: str, data: bytes) -> FrozenArtifact:
    if not isinstance(data, bytes):
        raise _fail("artifact data must be immutable bytes")
    return FrozenArtifact(role, repository_path, data, hashlib.sha256(data).hexdigest(), len(data))


def _roles(verifier_inputs: VerifierSnapshotInputs) -> dict[str, str]:
    try:
        if type(verifier_inputs) is not VerifierSnapshotInputs:
            raise ValueError("wrong verifier input type")
        if type(verifier_inputs.authority) is not AuthorityTuple:
            raise ValueError("wrong verifier authority type")
        if type(verifier_inputs.stable_census) is not StableCensusResult:
            raise ValueError("wrong stable census type")
        authority = verifier_inputs.authority
        try:
            computed_identity = derive_generation_identity(authority)
        except EvidenceDagError as exc:
            raise _fail("invalid verifier authority tuple") from exc
        if computed_identity != verifier_inputs.generation_identity:
            raise ValueError("generation identity differs from verifier authority")
        if not isinstance(authority.design_record_blob, str) or not _HEX40.fullmatch(authority.design_record_blob):
            raise ValueError("invalid verifier design-record blob")
        _validate_stable_census(verifier_inputs.stable_census)
        if not isinstance(verifier_inputs.generation_identity, str) or len(verifier_inputs.generation_identity) != 64 or any(c not in "0123456789abcdef" for c in verifier_inputs.generation_identity):
            raise ValueError("invalid generation identity")
        roles = verifier_inputs.canonical_roles
        if type(roles) is not tuple or any(type(x) is not tuple or len(x) != 2 or any(not isinstance(v, str) for v in x) for x in roles):
            raise ValueError("malformed canonical role tuple")
        result = dict(roles)
        if len(result) != len(roles):
            raise ValueError("duplicate canonical role")
        root = f"/private/tmp/vip-gate0/{verifier_inputs.generation_identity}/root"
        for name in _FIXED_ROOT_NAMES:
            role = f"roots.{name}"
            expected = f"{root}/roots/{name.replace('_', '-')}"
            if result.get(role) != expected:
                raise ValueError(f"noncanonical fixed role: {role}")
        for key in ("python_base_runtime_root", "python_run_scoped_venv_root", "ffmpeg_keg_root", "seed.python", "seed.ffmpeg", "seed.ffprobe"):
            if key not in result:
                raise ValueError(f"missing verifier source role: {key}")
        pyroot = result["python_base_runtime_root"]
        venv_root = result["python_run_scoped_venv_root"]
        froot = result["ffmpeg_keg_root"]
        py_parts = PurePosixPath(pyroot).parts
        ff_parts = PurePosixPath(froot).parts
        if (str(PurePosixPath(pyroot)) != pyroot or len(py_parts) != 6
                or py_parts[:5] != ("/", "opt", "homebrew", "Cellar", "python@3.14") or py_parts[5] in ("", ".", "..")
                or str(PurePosixPath(froot)) != froot or len(ff_parts) != 6
                or ff_parts[:5] != ("/", "opt", "homebrew", "Cellar", "ffmpeg") or ff_parts[5] in ("", ".", "..")
                or venv_root != f"/private/tmp/vip-gate0/{verifier_inputs.generation_identity}/runtime/python-venv"):
            raise ValueError("source roots are not canonical frozen formula domains")
        if _path_is_within(pyroot, venv_root) or _path_is_within(venv_root, pyroot):
            raise ValueError("Python scan roots overlap")
        if not _path_is_within(result["seed.python"], pyroot):
            raise ValueError("Python executable seed escapes the authorized base root")
        if result["seed.ffmpeg"] != froot.rstrip("/") + "/bin/ffmpeg" or result["seed.ffprobe"] != froot.rstrip("/") + "/bin/ffprobe":
            raise ValueError("tool seeds disagree with coherent keg root")
        return result
    except (TypeError, ValueError) as exc:
        raise _fail(f"invalid canonical verifier roles: {exc}") from exc


def _path_is_within(path: str, root: str) -> bool:
    return path == root or path.startswith(root.rstrip("/") + "/")


def _validate_stable_census(census: StableCensusResult) -> None:
    if (type(census.namespace_a) is not tuple or type(census.namespace_b) is not tuple
            or type(census.census_a_native_images) is not tuple
            or type(census.native_manifest_rows) is not tuple
            or type(census.native_manifest_bytes) is not bytes
            or type(census.native_manifest_sha256) is not str
            or type(census.native_member_count) is not int or census.native_member_count < 0):
        raise _fail("malformed stable census fields")
    if census.namespace_a != census.namespace_b:
        raise _fail("stable census namespace observations differ")
    for row in census.namespace_a + census.namespace_b:
        if (type(row) is not CensusNamespaceRow or type(row.scope_tag) is not CensusScopeTag
                or type(row.relative_path_utf8) is not bytes or type(row.entry_kind) is not EntryKind
                or (row.raw_link_target is not None and type(row.raw_link_target) is not bytes)
                or (row.canonicalization_result is not None and type(row.canonicalization_result) is not CanonicalizationResult)
                or (row.canonical_target is not None and not isinstance(row.canonical_target, PurePath))):
            raise _fail("malformed census namespace row")
        result = row.canonicalization_result
        if result is not None:
            if (type(result.family) is not CanonicalizationTerminalFamily
                    or (result.reason is not None and type(result.reason) is not CanonicalizationFailureReason)
                    or type(result.symlink_hops) is not int or not 0 <= result.symlink_hops <= 32
                    or result.canonical_target != row.canonical_target):
                raise _fail("malformed nested canonicalization result")
        if ((row.entry_kind is EntryKind.SYMLINK) != (result is not None)
                or (row.entry_kind is EntryKind.SYMLINK) != (row.raw_link_target is not None)):
            raise _fail("census symlink fields are inconsistent")
    for path, image in census.census_a_native_images:
        if not isinstance(path, PurePath) or type(image) is not bytes:
            raise _fail("malformed Census-A image row")
    for row in census.native_manifest_rows:
        if (type(row) is not NativeManifestRow or type(row.scope_tag) is not CensusScopeTag
                or type(row.relative_path_utf8) is not bytes or type(row.sha256_hex) is not str):
            raise _fail("malformed native manifest row")
    if census.native_member_count != len(census.native_manifest_rows):
        raise _fail("stable census member count mismatch")


def _identity(path: str, image: bytes) -> str:
    return f"{path}\n{hashlib.sha256(image).hexdigest()}"


def _read_host_native_image(path: Path) -> bytes:
    """The sole production host-byte observation leaf; callers pass canonical paths."""
    try:
        value = Path(path).read_bytes()
    except OSError as exc:
        raise _fail(f"cannot read admitted dependency image: {type(exc).__name__}") from exc
    if not isinstance(value, bytes):
        raise _fail("host image read did not return bytes")
    return value


def _canonical_host_path(path: str) -> str:
    try:
        candidate = Path(path)
        if not candidate.is_absolute():
            raise ValueError("dependency target is not absolute")
        resolved = candidate.resolve(strict=True)
        result = str(resolved)
        if not result.startswith("/") or "\x00" in result:
            raise ValueError("invalid canonical dependency path")
        return result
    except (OSError, RuntimeError, ValueError) as exc:
        raise _fail(f"dependency path resolution failed: {type(exc).__name__}") from exc


def _resolve_install_name(install_name: bytes, loader_path: str, executable_path: str, rpaths: tuple[bytes, ...]) -> tuple[str, ...]:
    try:
        name = install_name.decode("utf-8", "strict")
        if not name or "\x00" in name:
            raise ValueError("invalid install name")
        if name.startswith("/"):
            candidates = (name,)
        elif name == "@loader_path":
            candidates = (str(PurePosixPath(loader_path).parent),)
        elif name.startswith("@loader_path/"):
            candidates = (str(PurePosixPath(loader_path).parent / name[len("@loader_path/"):]),)
        elif name == "@executable_path":
            candidates = (str(PurePosixPath(executable_path).parent),)
        elif name.startswith("@executable_path/"):
            candidates = (str(PurePosixPath(executable_path).parent / name[len("@executable_path/"):]),)
        elif name == "@rpath/" or name.startswith("@rpath/"):
            suffix = name.removeprefix("@rpath/")
            expanded = []
            for raw_rpath in rpaths:
                entry = raw_rpath.decode("utf-8", "strict")
                if entry == "@loader_path":
                    base = str(PurePosixPath(loader_path).parent)
                elif entry.startswith("@loader_path/"):
                    base = str(PurePosixPath(loader_path).parent / entry[len("@loader_path/"):])
                elif entry == "@executable_path":
                    base = str(PurePosixPath(executable_path).parent)
                elif entry.startswith("@executable_path/"):
                    base = str(PurePosixPath(executable_path).parent / entry[len("@executable_path/"):])
                elif entry.startswith("/"):
                    base = entry
                else:
                    raise ValueError("unsupported rpath token")
                expanded.append(str(PurePosixPath(base) / suffix))
            candidates = tuple(expanded)
        else:
            raise ValueError("unrecognized dependency token")
        return tuple(dict.fromkeys(_canonical_host_path(x) for x in candidates if x))
    except (UnicodeDecodeError, OSError, RuntimeError, ValueError) as exc:
        raise _fail(f"dependency install-name resolution failed: {type(exc).__name__}") from exc


def _is_system(path: str) -> bool:
    return any(_path_is_within(path, root) for root in _SYSTEM_ROOTS)


def _derive_dependency_inventory_from_host(verifier_inputs: VerifierSnapshotInputs) -> tuple[DependencyInventoryEntry, ...]:
    """Derive closure from fixed seeds and Census-A images; no producer list participates."""
    roles = _roles(verifier_inputs)
    census = verifier_inputs.stable_census
    if type(verifier_inputs.verified_ffmpeg_bytes) is not bytes or type(verifier_inputs.verified_ffprobe_bytes) is not bytes:
        raise _fail("frozen tool seed bytes must be immutable")
    source_images: dict[str, bytes] = {}
    python_identities: set[str] = set()
    entries: dict[str, tuple[str, bytes]] = {}
    try:
        if type(census.census_a_native_images) is not tuple:
            raise ValueError("Census-A byte image collection is malformed")
        canonical_manifest = serialize_native_manifest(census)
        if (canonical_manifest != census.native_manifest_bytes
                or hashlib.sha256(canonical_manifest).hexdigest() != census.native_manifest_sha256
                or census.native_member_count != len(census.native_manifest_rows)):
            raise ValueError("Census-A native manifest does not match its immutable rows")
        expected_rows = []
        for path, image in census.census_a_native_images:
            text_path = str(path)
            if type(image) is not bytes or not text_path.startswith("/"):
                raise ValueError("Census-A image is not immutable or absolute")
            canonical = _canonical_host_path(text_path)
            if canonical != text_path:
                raise ValueError("Census-A image path is not canonical")
            if _path_is_within(canonical, roles["python_base_runtime_root"]):
                scope = CensusScopeTag.BASE_RUNTIME
                relative = canonical[len(roles["python_base_runtime_root"].rstrip("/")) + 1:]
            elif _path_is_within(canonical, roles["python_run_scoped_venv_root"]):
                scope = CensusScopeTag.RUN_SCOPED_VENV
                relative = canonical[len(roles["python_run_scoped_venv_root"].rstrip("/")) + 1:]
            else:
                raise ValueError("Census-A image outside the two authorized Python roots")
            expected_rows.append(NativeManifestRow(scope, relative.encode("utf-8", "strict"), hashlib.sha256(image).hexdigest()))
            if canonical in source_images and source_images[canonical] is not image:
                raise ValueError("duplicate Census-A source has divergent byte image")
            source_images[canonical] = image
            identity = _identity(canonical, image)
            python_identities.add(identity)
        row_key = lambda row: (row.scope_tag.value.encode("ascii"), row.relative_path_utf8, row.sha256_hex.encode("ascii"))
        if tuple(sorted(expected_rows, key=row_key)) != tuple(sorted(census.native_manifest_rows, key=row_key)):
            raise ValueError("Census-A rows do not describe the retained first byte images")
    except (OSError, RuntimeError, ValueError) as exc:
        raise _fail(f"invalid Census-A source images: {exc}") from exc

    python_seed = _canonical_host_path(roles["seed.python"])
    python_seed_image = source_images.get(python_seed)
    if (python_seed_image is None
            or hashlib.sha256(python_seed_image).hexdigest() != _PYTHON_SEED_SHA256):
        raise _fail("Python executable seed is absent from Census-A or conflicts with its frozen digest")
    python_seed_identity = _identity(python_seed, python_seed_image)
    entries[python_seed_identity] = ("PYTHON", python_seed_image)

    # P25 never infers a Python-family license from lexical root membership alone.
    if entries:
        baseline = getattr(census, "native_manifest_sha256", None)
        echo = None
        # The owner-pinned profile is represented only by S4; this derivation helper
        # is called again by the public constructor after its S4 echo was validated.
        # Stable census content remains a verifier input, not a producer selector.
        if not isinstance(baseline, str) or len(baseline) != 64:
            raise _fail("Census-A native manifest lacks a verifier digest")

    seed_paths = (roles["seed.ffmpeg"], roles["seed.ffprobe"])
    seed_images = (verifier_inputs.verified_ffmpeg_bytes, verifier_inputs.verified_ffprobe_bytes)
    seed_cache: dict[str, bytes] = {}
    expected_digests = (_FFMPEG_SEED_SHA256, _FFPROBE_SEED_SHA256)
    for path, image, expected_digest in zip(seed_paths, seed_images, expected_digests):
        canonical = _canonical_host_path(path)
        if not _path_is_within(canonical, roles["ffmpeg_keg_root"]):
            raise _fail("tool seed escapes coherent FFmpeg keg")
        if hashlib.sha256(image).hexdigest() != expected_digest:
            raise _fail("tool seed byte image disagrees with the frozen profile digest")
        if canonical in seed_cache and seed_cache[canonical] != image:
            raise _fail("tool seed canonical identity has conflicting bytes")
        seed_cache[canonical] = image
        source_images.setdefault(canonical, image)

    # Keep originating executable context in the visited key. All discovered
    # non-system sources are byte-cached by canonical identity and read once.
    queue: list[tuple[str, str, str]] = [(path, path, "TOOL") for path in seed_paths]
    queue.append((python_seed, python_seed, "PYTHON"))
    visited: set[tuple[str, str]] = set()
    edge_targets: dict[tuple[str, bytes], str] = {}
    while queue:
        source, origin, family = queue.pop(0)
        source = _canonical_host_path(source)
        state = (source, origin)
        if state in visited:
            continue
        visited.add(state)
        if source not in source_images:
            image = _read_host_native_image(Path(source))
            source_images[source] = image
        image = source_images[source]
        parsed = MACHO_NATIVE_CONTAINER_PARSE_V1(image)
        rpaths = tuple(command.rpath_value for command in parsed.load_commands if command.rpath_value is not None)
        edge_commands = tuple(command for command in parsed.load_commands if command.dependency_install_name is not None)
        if tuple(command.dependency_install_name for command in edge_commands) != parsed.dependency_edges:
            raise _fail("parser dependency edge projection is inconsistent")
        for command in edge_commands:
            install_name = command.dependency_install_name
            targets = _resolve_install_name(install_name, source, origin, rpaths)
            if not targets:
                raise _fail("dependency edge has no candidate targets")
            if len(targets) != 1:
                raise _fail("dependency edge has ambiguous canonical targets")
            target = targets[0]
            if _is_system(target):
                continue
            python_member_identity = _identity(target, source_images[target]) if target in source_images else None
            if python_member_identity not in python_identities and not _path_is_within(target, _CELLAR_ROOT):
                raise _fail("non-system dependency target is outside Domain P membership and Domain H")
            if target not in source_images:
                source_images[target] = _read_host_native_image(Path(target))
            target_image = source_images[target]
            identity = _identity(target, target_image)
            if identity in python_identities:
                target_family = "PYTHON"
            elif _path_is_within(target, _CELLAR_ROOT):
                target_family = "TOOL"
            else:
                raise _fail("non-system dependency target lacks verified family authority")
            logical_edge = (_identity(source, image) + f"\n{command.command_value:08x}", install_name)
            prior = edge_targets.setdefault(logical_edge, identity)
            if prior != identity:
                raise _fail("one logical dependency edge diverges across contexts")
            entries.setdefault(identity, (target_family, target_image))
            queue.append((target, origin, family))

    ordered = sorted(entries.items(), key=lambda pair: (pair[1][0].encode("ascii"), pair[0].encode("utf-8")))
    family_indices = {"TOOL": 0, "PYTHON": 0}
    result = []
    for identity, (family, image) in ordered:
        role_family = family.lower()
        index = family_indices[family]
        family_indices[family] += 1
        result.append(DependencyInventoryEntry(family, identity, f"dependency-roots/{role_family}/{index}", image))
    return tuple(result)


def render_s2_from_s1(s1: FrozenArtifact) -> FrozenArtifact:
    """Render the exact entitlement plist from one frozen S1 artifact."""
    if type(s1) is not FrozenArtifact or s1.role != "S1" or type(s1.data) is not bytes:
        raise EvidenceDagError(EvidenceFailureCode.RENDER_INPUT_NOT_FROZEN, "S2 renderer requires the exact frozen S1 artifact")
    if s1.octets != len(s1.data) or s1.sha256 != hashlib.sha256(s1.data).hexdigest():
        raise EvidenceDagError(EvidenceFailureCode.RENDER_INPUT_NOT_FROZEN, "S1 artifact digest or length is invalid")
    try:
        value = json.loads(s1.data.decode("utf-8"))
        roots = value["roots"]
        tool = value["tool_dependency_roots"]
        python = value["python_dependency_roots"]
        if type(roots) is not dict or type(tool) is not list or type(python) is not list:
            raise ValueError("bad S1 projection types")
        reads = [roots[f"roots.{name}"] for name in _FIXED_ROOT_NAMES if name != "output"]
        reads.extend(tool)
        reads.extend(python)
        readonly = sorted({path.rstrip("/") + "/" for path in reads})
        output = roots["roots.output"].rstrip("/") + "/"
        plist = {
            "com.apple.security.app-sandbox": True,
            "com.apple.security.temporary-exception.files.absolute-path.read-only": readonly,
            "com.apple.security.temporary-exception.files.absolute-path.read-write": [output],
        }
        data = plistlib.dumps(plist, fmt=plistlib.FMT_XML, sort_keys=True)
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceDagError(EvidenceFailureCode.RENDER_INPUT_NOT_FROZEN, f"invalid frozen S1: {exc}") from exc
    return _artifact("S2", "S2.plist", data)


def derive_frozen_snapshots(verifier_inputs: VerifierSnapshotInputs, producer_inputs: ProducerSnapshotInputs) -> FrozenSnapshotSet:
    if type(producer_inputs) is not ProducerSnapshotInputs:
        raise _fail("invalid producer snapshot input")
    roles = _roles(verifier_inputs)
    if not isinstance(producer_inputs.argv, tuple) or any(not isinstance(x, str) for x in producer_inputs.argv):
        raise _fail("producer argv malformed")
    if (not isinstance(producer_inputs.execution_mode, str)
            or producer_inputs.execution_mode not in EXECUTION_MODES
            or not isinstance(producer_inputs.target_safety_validation_ref, str)
            or not producer_inputs.target_safety_validation_ref.strip()):
        raise EvidenceDagError(EvidenceFailureCode.ENVELOPE_REFERENCE_NOT_ACCEPTED, "P24 envelope references are required")
    try:
        s4_echo = validate_s4_echo(
            producer_inputs.s4_bytes,
            verifier_python_base_runtime_root=roles["python_base_runtime_root"],
            verifier_ffmpeg_keg_root=roles["ffmpeg_keg_root"],
        )
    except EvidenceDagError:
        raise

    effective_output = roles["roots.output"]
    if (producer_inputs.declared_output_root != effective_output
            or producer_inputs.output_root_provenance_token != "VERIFIER_MATERIALIZED_CANONICAL_ROOT_V1"):
        raise EvidenceDagError(EvidenceFailureCode.OUTPUT_ROOT_AMBIGUOUS, "declared output root or provenance token differs from the verifier role")
    census = verifier_inputs.stable_census
    if (s4_echo.get("python_native_closure_baseline_state") != "MEASURED_AND_OWNER_PINNED"
            or _OWNER_PINNED_NATIVE_PROFILE_V1 is None):
        raise _fail("owner-pinned Python native closure baseline is NOT_OBSERVED")
    owner_profile = _OWNER_PINNED_NATIVE_PROFILE_V1
    if (type(owner_profile) is not tuple or len(owner_profile) != 2
            or type(owner_profile[0]) is not str or not _HEX64.fullmatch(owner_profile[0])
            or type(owner_profile[1]) is not int or owner_profile[1] <= 0
            or s4_echo.get("python_native_closure_baseline_sha256") != owner_profile[0]
            or s4_echo.get("python_native_closure_baseline_member_count") != owner_profile[1]
            or census.native_manifest_sha256 != owner_profile[0]
            or census.native_member_count != owner_profile[1]):
        raise _fail("Census-A native profile differs from the independently owner-pinned baseline")

    inventory = _derive_dependency_inventory_from_host(verifier_inputs)
    root_value = {f"roots.{name}": roles[f"roots.{name}"] for name in _FIXED_ROOT_NAMES}
    tool_roots = [x.materialized_role for x in inventory if x.family == "TOOL"]
    python_roots = [x.materialized_role for x in inventory if x.family == "PYTHON"]
    s1_value = {
        "roots": root_value,
        "tool_dependency_roots": tool_roots,
        "python_dependency_roots": python_roots,
    }
    s1 = _artifact("S1", "S1.json", _canonical_json(s1_value))
    s2 = render_s2_from_s1(s1)

    authority = {
        "base_controller_commit": verifier_inputs.authority.base_controller_commit,
        "applicable_spec_blob": verifier_inputs.authority.applicable_spec_blob,
        "applicable_plan_blob": verifier_inputs.authority.applicable_plan_blob,
        "design_record_blob": verifier_inputs.authority.design_record_blob,
        "generation_ordinal": verifier_inputs.authority.generation_ordinal,
        "generation_identity": verifier_inputs.generation_identity,
    }
    s3_value = {
        "argv": list(producer_inputs.argv),
        "declared_output_root": producer_inputs.declared_output_root,
        "output_root_provenance_token": producer_inputs.output_root_provenance_token,
        "execution_mode": producer_inputs.execution_mode,
        "target_safety_validation_ref": producer_inputs.target_safety_validation_ref,
        "authority": authority,
    }
    s3 = _artifact("S3", "S3.json", _canonical_json(s3_value))
    if s4_echo.get("optional_tool_seed_registry_v1") != list(_OPTIONAL_SEEDS_V1):
        raise _fail("optional seed registry must remain empty")
    s4 = _artifact("S4", "S4.json", producer_inputs.s4_bytes)
    return FrozenSnapshotSet(s1, s2, s3, s4, inventory)
