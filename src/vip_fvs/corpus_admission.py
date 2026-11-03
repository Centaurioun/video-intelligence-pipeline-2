"""Ephemeral, synthetic-only preflight bindings for P2 entry boundaries.

This carries a checked P1 synthetic attestation through one in-memory operation.
It is test plumbing, not a real admission grant or trust anchor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from . import corpus_separation as cs


class CorpusAdmissionError(ValueError):
    """Stable refusal for a malformed or mismatched synthetic preflight."""


@dataclass(frozen=True)
class AdmissionBinding:
    revision_id: str
    source_sha256: str
    authorization: Mapping[str, Any]
    locator: str = ""


_CONTEXT_SEAL = object()


@dataclass(frozen=True)
class SyntheticPreflightContext:
    operation: str
    bindings: tuple[tuple[str, str, str, str], ...]
    output_root: str
    plan_digest: str | None
    manifest_digest: str | None
    attestation_digests: tuple[str, ...]
    preview_authorization_digest: str | None = None
    evidence_state: str = "SYNTHETIC_ONLY"
    authenticity_status: str = "SYNTHETIC_TRUST_DOUBLE_ONLY"
    _seal: object = field(default=None, repr=False, compare=False)


def _refuse() -> CorpusAdmissionError:
    return CorpusAdmissionError("CORPUS_SEPARATION_DECLARATION_INVALID")


def _binding_key(binding: AdmissionBinding) -> tuple[str, str, str, str]:
    if (not isinstance(binding, AdmissionBinding)
            or not isinstance(binding.revision_id, str) or not binding.revision_id
            or not isinstance(binding.source_sha256, str) or len(binding.source_sha256) != 64
            or any(c not in "0123456789abcdef" for c in binding.source_sha256)
            or not isinstance(binding.authorization, Mapping)
            or not isinstance(binding.locator, str)):
        raise _refuse()
    try:
        scope_digest = cs.authorization_scope_digest(binding.authorization)
    except (TypeError, ValueError) as exc:
        raise _refuse() from exc
    return (binding.revision_id, binding.source_sha256, scope_digest, binding.locator)


def check_synthetic_preflight(
    attestations: Sequence[Mapping[str, Any]], *,
    bindings: Sequence[AdmissionBinding], operation: str, output_root: str | Path,
    plan_digest: str | None = None, manifest_digest: str | None = None,
    preview_authorization_digest: str | None = None,
) -> SyntheticPreflightContext:
    """Validate P1 attestations and bind ordered candidates to one operation."""
    if not isinstance(attestations, Sequence) or isinstance(attestations, (str, bytes)):
        raise _refuse()
    if not attestations:
        raise CorpusAdmissionError("CORPUS_SEPARATION_ATTESTATION_REQUIRED")
    if (not isinstance(bindings, Sequence)
            or not isinstance(operation, str) or not operation or len(attestations) != len(bindings)
            or (plan_digest is not None and (not isinstance(plan_digest, str) or len(plan_digest) != 64
                                             or any(c not in "0123456789abcdef" for c in plan_digest)))
            or (manifest_digest is not None and (not isinstance(manifest_digest, str) or len(manifest_digest) != 64
                                                 or any(c not in "0123456789abcdef" for c in manifest_digest)))
            or (preview_authorization_digest is not None and
                (not isinstance(preview_authorization_digest, str) or len(preview_authorization_digest) != 64
                 or any(c not in "0123456789abcdef" for c in preview_authorization_digest)))):
        raise _refuse()
    keys = tuple(_binding_key(item) for item in bindings)
    digests: list[str] = []
    try:
        for attestation, (revision_id, source_sha256, auth_digest, _locator) in zip(attestations, keys):
            cs.validate_attestation(attestation)
            if (attestation.get("authenticity_status") != "SYNTHETIC_TRUST_DOUBLE_ONLY"
                    or attestation.get("candidate_revision_id") != revision_id
                    or attestation.get("candidate_source_sha256") != source_sha256
                    or attestation.get("candidate_authorization_digest") != auth_digest
                    or attestation.get("byte_disjoint_status") != "VERIFIED_DISJOINT_SYNTHETIC"
                    or attestation.get("declared_relations_status") != "VERIFIED_DISJOINT_SYNTHETIC"):
                raise _refuse()
            digests.append(str(attestation["attestation_digest"]))
    except cs.CorpusSeparationError as exc:
        raise CorpusAdmissionError(str(exc)) from exc
    try:
        normalized_output = str(Path(output_root).resolve())
    except (TypeError, ValueError, OSError) as exc:
        raise _refuse() from exc
    return SyntheticPreflightContext(
        operation=operation, bindings=keys, output_root=normalized_output,
        plan_digest=plan_digest, manifest_digest=manifest_digest,
        preview_authorization_digest=preview_authorization_digest,
        attestation_digests=tuple(digests), _seal=_CONTEXT_SEAL,
    )


def require_synthetic_preflight(
    context: SyntheticPreflightContext, *, bindings: Sequence[AdmissionBinding],
    operation: str, output_root: str | Path, plan_digest: str | None = None,
    manifest_digest: str | None = None, preview_authorization_digest: str | None = None,
) -> None:
    """Rebind checked context at the source entry boundary."""
    if (not isinstance(context, SyntheticPreflightContext) or context._seal is not _CONTEXT_SEAL
            or context.evidence_state != "SYNTHETIC_ONLY"
            or context.authenticity_status != "SYNTHETIC_TRUST_DOUBLE_ONLY"
            or len(context.attestation_digests) != len(context.bindings)
            or not context.attestation_digests
            or any(not isinstance(value, str) or len(value) != 64
                   or any(c not in "0123456789abcdef" for c in value)
                   for value in context.attestation_digests)):
        raise _refuse()
    try:
        keys = tuple(_binding_key(item) for item in bindings)
    except (TypeError, AttributeError) as exc:
        raise _refuse() from exc
    try:
        normalized_output = str(Path(output_root).resolve())
    except (TypeError, ValueError, OSError) as exc:
        raise _refuse() from exc
    if (context.operation != operation or context.bindings != keys
            or context.output_root != normalized_output
            or context.plan_digest != plan_digest or context.manifest_digest != manifest_digest
            or context.preview_authorization_digest != preview_authorization_digest):
        raise _refuse()


__all__ = [
    "AdmissionBinding", "CorpusAdmissionError", "SyntheticPreflightContext",
    "check_synthetic_preflight", "require_synthetic_preflight",
]
