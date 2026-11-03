"""Explicit-handoff-only N4B sealing into an additive synthetic Git tree."""
from __future__ import annotations

import hashlib

from gate0.feasibility import macos_stage_b_evidence_anchor as anchor_mod
from gate0.feasibility import macos_stage_b_evidence_git as git_mod
from gate0.feasibility import macos_stage_b_evidence_boundary as boundary
from gate0.feasibility.macos_stage_b_evidence_constants import (
    EvidenceDagError, EvidenceFailureCode, FrozenArtifact, N4ASealHandoff,
    S7AnchorCreateResult, SealResult, SignedImageProjection,
)

_FAILURE = EvidenceFailureCode.SIGNED_BYTES_NOT_VERIFIER_DERIVED
_MEMBER_FIELDS = (
    ("executable_code_region", "executable-code-region.bin", "executable_code_region_bytes"),
    ("info_plist", "Info.plist", "info_plist_bytes"),
    ("code_resources", "CodeResources", "code_resources_bytes"),
    ("superblob_index", "superblob-index.bin", "superblob_index_bytes"),
    ("code_directory", "CodeDirectory", "code_directory_bytes"),
    ("entitlements_blob", "Entitlements.blob", "entitlements_blob_bytes"),
    ("der_entitlements_blob", "DER-Entitlements.blob", "der_entitlements_blob_bytes"),
    ("identity", "identity.json", "canonical_identity_json_bytes"),
)


def _fail(reason: str) -> EvidenceDagError:
    return EvidenceDagError(_FAILURE, reason)


def _git_input(argv: tuple[str, ...], input_bytes: bytes | None = None) -> bytes:
    return anchor_mod._git_input(argv, git_mod._root(), input_bytes)


def _validate_projection(projection: SignedImageProjection) -> tuple[tuple[str, bytes], ...]:
    if type(projection) is not SignedImageProjection:
        raise _fail("handoff projection has invalid type")
    members = []
    for key, name, field in _MEMBER_FIELDS:
        value = getattr(projection, field)
        if type(value) is not bytes or not value:
            raise _fail(f"NOT_OBSERVED: projection member {key} is unavailable")
        members.append((f"S9/{name}", value))
    if len({path for path, _ in members}) != 8:
        raise _fail("projection member paths are not unique")
    return tuple(members)


def _tree_entries(commit_sha: str) -> tuple[tuple[str, str, str], ...]:
    raw = git_mod._run_git(("ls-tree", "-rz", "--full-tree", commit_sha), git_mod._root()).stdout
    rows = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, name = record.split(b"\t", 1)
        mode, kind, oid = meta.split(b" ", 2)
        if kind != b"blob" or mode not in (b"100644", b"100755"):
            raise _fail("S7 contains a non-blob or unsupported entry")
        rows.append((name.decode("utf-8", "strict"), mode.decode("ascii"), oid.decode("ascii")))
    return tuple(rows)


def seal_n4b(s7: S7AnchorCreateResult, handoff: N4ASealHandoff) -> SealResult:
    """Claim the exact registered handoff, then commit its eight bytes under S9/."""
    if type(s7) is not S7AnchorCreateResult or type(handoff) is not N4ASealHandoff:
        raise _fail("N4B seal requires exact S7 and handoff types")
    context = handoff.source_application
    # Resolve exact owning context through the source's verifier-owned binding.
    binding = boundary._CAPTURE_BINDINGS.get(id(context))
    if binding is None or binding.application is not context:
        raise _fail("handoff application has no registered repository context")
    repository_context = binding.context
    boundary._claim_n4a_lifecycle(
        handoff.capability, repository_context, claimant="n4b_seal", handoff=handoff,
    )
    # Claim precedes all content validation. No registry primitive slot is read here.
    if (s7.commit_sha != repository_context.evaluation_commit
            or s7.parent_commit_sha != repository_context.base_controller_commit):
        raise _fail("S7 anchor does not match handoff repository context")
    s7_artifacts = tuple(
        FrozenArtifact(role, path, git_mod.read_blob_at(s7.commit_sha, path),
                      hashlib.sha256(git_mod.read_blob_at(s7.commit_sha, path)).hexdigest(),
                      len(git_mod.read_blob_at(s7.commit_sha, path)))
        for role, path in zip(("S1", "S2", "S3", "S4"), ("S1.json", "S2.plist", "S3.json", "S4.json"))
    )
    if not anchor_mod.verify_s7_anchor(s7, s7_artifacts).passed:
        raise _fail("S7 anchor failed exact reread validation")
    members = _validate_projection(handoff.projection)
    inherited = _tree_entries(s7.commit_sha)
    inherited_names = {row[0] for row in inherited}
    additions = {path for path, _ in members}
    if inherited_names & additions:
        raise _fail("S7 already contains an S9 projection path")
    # The validated S7 contract is a closed root tree of four files. Build its
    # additive S9 child tree first, then add that tree entry without rewriting S7.
    added_oids = {}
    s9_rows = []
    for path, data in members:
        oid = anchor_mod._decode_oid(_git_input(("hash-object", "-w", "--stdin"), data), "blob")
        added_oids[path] = oid
        s9_rows.append(f"100644 blob {oid}\t{path.split('/', 1)[1]}\n".encode("utf-8"))
    s9_tree = anchor_mod._decode_oid(_git_input(("mktree",), b"".join(sorted(s9_rows))), "tree")
    rows = [f"{mode} blob {oid}\t{name}\n".encode("utf-8") for name, mode, oid in inherited]
    rows.append(f"040000 tree {s9_tree}\tS9\n".encode("ascii"))
    tree_sha = anchor_mod._decode_oid(_git_input(("mktree",), b"".join(sorted(rows))), "tree")
    commit_sha = anchor_mod._decode_oid(
        _git_input(("commit-tree", tree_sha, "-p", s7.commit_sha, "-m", "Gate-0 N4B additive seal")),
        "commit",
    )
    if git_mod.commit_parent(commit_sha) != s7.commit_sha or git_mod.commit_tree(commit_sha) != tree_sha:
        raise _fail("B commit parent or tree differs from validated S7 addition")
    committed_entries = _tree_entries(commit_sha)
    if len(committed_entries) != len(inherited) + 8:
        raise _fail("B tree is not exactly additive")
    committed_map = {name: (mode, oid) for name, mode, oid in committed_entries}
    if any(committed_map.get(name) != (mode, oid) for name, mode, oid in inherited):
        raise _fail("an inherited S7 tree entry changed")
    for path, data in members:
        if committed_map.get(path) != ("100644", added_oids[path]):
            raise _fail("committed projection path or mode differs")
        if git_mod.read_blob_at(commit_sha, path) != data:
            raise _fail("committed projection bytes differ from explicit handoff")
    return SealResult(commit_sha, tree_sha, s7.commit_sha, tuple(path for path, _ in members),
                      hashlib.sha256(handoff.projection.canonical_identity_json_bytes).hexdigest())
