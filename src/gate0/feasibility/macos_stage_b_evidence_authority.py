"""Verifier-derived authority and coherence checks for S3/S4."""
from __future__ import annotations

import hashlib
import json
import re
import struct

from gate0.feasibility.macos_stage_b_evidence_constants import (
    AuthorityTuple, EvidenceDagError, EvidenceFailureCode,
)
from gate0.feasibility.macos_stage_b_evidence_git import (
    blob_id_at, reachable_committed_generation_identities,
)

_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
PLAN_PATH = "docs/superpowers/plans/2026-09-14-gate0-stage-b-c2-v3-implementation-plan.md"
SPEC_PATH = "docs/superpowers/specs/2026-09-20-gate0-recovery-evidence-dag-design.md"
DESIGN_RECORD_PATH = "docs/gates/gate0/rulings/2026-09-23-rr17-final-specification-closure-design-ruling.md"


def _fail(detail: str, code=EvidenceFailureCode.GENERATION_IDENTITY_COLLISION):
    raise EvidenceDagError(code, detail)


def _sha256_generation_identity_payload(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def derive_generation_identity(authority: AuthorityTuple) -> str:
    if type(authority) is not AuthorityTuple:
        _fail("invalid generation authority")
    ids = (authority.base_controller_commit, authority.applicable_spec_blob,
           authority.applicable_plan_blob)
    for value in ids:
        if not isinstance(value, str) or not _HEX40.fullmatch(value):
            _fail("invalid generation authority object id")
        raw = value.encode("ascii")
        if len(raw) > 0xFFFF:
            _fail("generation authority identity exceeds u16 length")
    ordinal = authority.generation_ordinal
    if type(ordinal) is not int or not 1 <= ordinal <= 0xFFFFFFFFFFFFFFFF:
        _fail("invalid generation ordinal")
    payload = bytearray(b"G0_GENERATION_IDENTITY_V1\0")
    for value in ids:
        raw = value.encode("ascii")
        payload.extend(struct.pack(">H", len(raw)))
        payload.extend(raw)
    payload.extend(struct.pack(">Q", ordinal))
    return _sha256_generation_identity_payload(bytes(payload))


def derive_authority_tuple(base_controller_commit: str, evaluation_commit: str) -> AuthorityTuple:
    """Resolve authority blobs only from the frozen controller commit."""
    if not isinstance(base_controller_commit, str) or not _HEX40.fullmatch(base_controller_commit):
        _fail("invalid controller commit")
    try:
        spec = blob_id_at(base_controller_commit, SPEC_PATH)
        plan = blob_id_at(base_controller_commit, PLAN_PATH)
        design = blob_id_at(base_controller_commit, DESIGN_RECORD_PATH)
        prior = reachable_committed_generation_identities(evaluation_commit)
    except EvidenceDagError:
        raise
    except Exception as exc:
        _fail(f"authority resolution failed: {type(exc).__name__}")
    return AuthorityTuple(base_controller_commit, spec, plan, design, len(set(prior)) + 1)


def derive_generation_authority(base_controller_commit: str, evaluation_commit: str) -> tuple[AuthorityTuple, str]:
    authority = derive_authority_tuple(base_controller_commit, evaluation_commit)
    identity = derive_generation_identity(authority)
    if identity in reachable_committed_generation_identities(evaluation_commit):
        _fail("generation identity has already been committed")
    return authority, identity


def verify_s3_authority_echo(s3: dict, authority: AuthorityTuple, generation_identity: str) -> None:
    """S3 is an echo surface; compare its closed authority values to verifier inputs."""
    expected = {
        "base_controller_commit": authority.base_controller_commit,
        "applicable_spec_blob": authority.applicable_spec_blob,
        "applicable_plan_blob": authority.applicable_plan_blob,
        "design_record_blob": authority.design_record_blob,
        "generation_ordinal": authority.generation_ordinal,
        "generation_identity": generation_identity,
    }
    if type(s3) is not dict or any(type(s3.get(k)) is not type(v) or s3.get(k) != v for k, v in expected.items()):
        raise EvidenceDagError(EvidenceFailureCode.AUTHORITY_ECHO_MISMATCH, "S3 authority echo differs from verifier-derived values")


S4_NOT_OBSERVED_KEYS_V1 = frozenset("""python_version python_architecture python_formula_lineage python_executable_sha256 python_lock_path python_lock_sha256 python_base_runtime_root_identity python_base_runtime_root python_native_runtime_closure_format python_native_closure_baseline_state ffmpeg_version ffmpeg_architecture ffmpeg_executable_sha256 ffprobe_version ffprobe_architecture ffprobe_executable_sha256 ffmpeg_keg_root_identity ffmpeg_keg_root native_execution_architecture optional_tool_seed_registry_v1""".split())
S4_MEASURED_AND_OWNER_PINNED_KEYS_V1 = S4_NOT_OBSERVED_KEYS_V1 | frozenset({"python_native_closure_baseline_sha256", "python_native_closure_baseline_member_count"})


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON member")
        result[key] = value
    return result


def validate_s4_echo(value: dict | bytes | str, *, verifier_python_base_runtime_root: str,
                     verifier_ffmpeg_keg_root: str) -> dict:
    """Validate S4 closure and compare root echoes to independently derived verifier inputs."""
    try:
        if (not isinstance(verifier_python_base_runtime_root, str) or not verifier_python_base_runtime_root
                or not isinstance(verifier_ffmpeg_keg_root, str) or not verifier_ffmpeg_keg_root):
            raise ValueError("missing verifier-derived root")
        if isinstance(value, bytes):
            value = value.decode("utf-8", "strict")
        if isinstance(value, str):
            value = json.loads(value, object_pairs_hook=_unique_object)
        if type(value) is not dict or "a2r_m1r_echo" not in value or type(value["a2r_m1r_echo"]) is not dict:
            raise ValueError("missing echo object")
        echo = value["a2r_m1r_echo"]
        state = echo.get("python_native_closure_baseline_state")
        required = S4_NOT_OBSERVED_KEYS_V1 if state == "NOT_OBSERVED" else S4_MEASURED_AND_OWNER_PINNED_KEYS_V1 if state == "MEASURED_AND_OWNER_PINNED" else frozenset()
        if not required or set(echo) != required:
            raise ValueError("S4 key set mismatch")
        if state == "NOT_OBSERVED":
            if "python_native_closure_baseline_sha256" in echo or "python_native_closure_baseline_member_count" in echo:
                raise ValueError("NOT_OBSERVED carries baseline")
        else:
            digest, count = echo["python_native_closure_baseline_sha256"], echo["python_native_closure_baseline_member_count"]
            if not isinstance(digest, str) or not _HEX64.fullmatch(digest) or type(count) is not int or count < 0:
                raise ValueError("invalid owner-pinned baseline")
        fixed = {
            "python_version": "3.14.7", "python_architecture": "arm64",
            "python_formula_lineage": "python@3.14",
            "python_executable_sha256": "87d4df53fd91304be5bac391fb204643c36b7df2023c04a0953bcbc7d4fdf634",
            "python_lock_path": "requirements/gate0-macos-stage-a.lock",
            "python_lock_sha256": "d20752c0a55fa9552303bce6372fdb2172934bd95ec21e26463af997d77adfbc",
            "python_base_runtime_root_identity": "PYTHON_BASE_RUNTIME_ROOT_V1",
            "python_native_runtime_closure_format": "PYTHON_NATIVE_RUNTIME_CLOSURE_V1",
            "ffmpeg_version": "9.0.1", "ffmpeg_architecture": "arm64",
            "ffmpeg_executable_sha256": "9f5ddd4f8b36eb07b0c5d60ab6ea1e618bedd70bc45feab82b4dc23be1596ad1",
            "ffprobe_version": "9.0.1", "ffprobe_architecture": "arm64",
            "ffprobe_executable_sha256": "0ecd5e1affb1466b129b4f65bee261e9ab625c4d4a2e7c3e9089f63d44808605",
            "ffmpeg_keg_root_identity": "HOMEBREW_FFMPEG_KEG_ROOT_V1",
            "native_execution_architecture": "arm64",
        }
        if any(echo.get(key) != expected for key, expected in fixed.items()):
            raise ValueError("S4 conflicts with frozen verifier profile")
        if (echo.get("python_base_runtime_root") != verifier_python_base_runtime_root
                or echo.get("ffmpeg_keg_root") != verifier_ffmpeg_keg_root):
            raise ValueError("S4 root echo conflicts with verifier-derived root")
        for key, item in echo.items():
            if key == "optional_tool_seed_registry_v1":
                if type(item) is not list or item != []: raise ValueError("invalid optional seed registry")
            elif key == "python_native_closure_baseline_member_count":
                if type(item) is not int or item < 0: raise ValueError("invalid member count")
            elif not isinstance(item, str):
                raise ValueError("wrong S4 field type")
        return echo
    except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceDagError(EvidenceFailureCode.DEPENDENCY_INVENTORY_DERIVATION_INVALID, f"invalid S4 echo: {exc}") from exc
