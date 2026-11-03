"""Deterministic Gate-0 configuration-freeze *readiness* inspector (P-09).

This module is Gate-0 D-1 preparation-only tooling.  It computes the canonical
configuration digest, verifies caller-supplied observed digests against the
declared frozen configuration, and reports every unresolved input/model/policy/
sandbox/blinding digest identity.  It deliberately cannot "freeze" a config:

* ``freeze_state`` is always ``NOT_FROZEN``; a successful inspection only means
  the metadata is ready for an Owner/D-2/D-3 freeze review.
* ``authentic`` is always ``False``.  A configuration assembled from generated or
  synthetic metadata is never labelled as an approved real configuration, and a
  clean audit carries no signed approval and no Gate verdict.
* ``gate_verdict`` is always ``NOT_RUN`` under D-1.
* ``execution_authorized=True`` is echoed but is *not* a trust grant: the output
  stays preparation-only and ``execution_activation`` stays unavailable.
* No configured input root, policy root or model asset is opened; the only file
  read is the frozen JSON schema used for read-only validation.
* Nothing is downloaded, imported from the network or inferred; all model
  dimensions/versions/identities remain declarative, unverified metadata.

Observed-digest input contract
------------------------------
``observed_digests`` maps ``"<stage>:<identity>"`` to a caller-supplied
lowercase SHA-256 hex digest.  ``<identity>`` must be one of the canonical digest
identities reported in ``digest_entries``, including the required policy-root
identity ``policy.review_input.authorized_root`` (the digest of the declared
review-root path).  ``<stage>`` is the freeze stage at which that digest may
legitimately be computed:

* ``pre_inventory``  - declared roots/identities before inventory
* ``post_inventory`` - source-manifest digest (never before inventory)
* ``model``          - model identity/weights/processor digests
* ``policy``         - policy egress manifest and review-root identity
* ``sandbox``        - bwrap/interpreter digests and launcher policy digests
* ``blinding``       - blind mapping digest

Every observed value is unverified caller metadata; the inspector reports that
source explicitly and distinguishes "never supplied" from "supplied but
invalid".  Unknown keys, duplicate/ambiguous freeze points, wrong-stage
observations, non-lowercase or all-zero digests, substitutes, mismatched policy
roots and source-manifest revisions all fail closed into a deterministic,
sorted failure/need list.

Additional fail-closed preparation rules
----------------------------------------
* ``corpus.source_root`` must be a concrete absolute path; the frozen template
  value (``inputs``) is a placeholder, not an authorized corpus root.
* ``sandbox.read_only_mounts`` / ``sandbox.writable_mounts`` must match the
  frozen launcher mount policy exactly.
* Readiness is configuration-metadata-only: the dependency lock is not
  validated here (see ``provenance.dependency_lock_validation``), and
  ``approval`` is always ``NOT_GRANTED``.

The frozen schema and invariants are validated through the existing
``gate0.config`` loader validators (read-only) so this tool cannot drift from the
contract-frozen configuration contract; public canonical hashing reuses
``gate0.config.canonical_json_bytes`` byte-for-byte (including its trailing LF).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import config as _config
from .identity import SHA256_PATTERN, digest_bytes
from .launcher_attestation import (
    MOUNT_POLICY,
    expected_argv_digest,
    expected_mount_policy_digest,
)

SCHEMA_VERSION = "gate0.config-freeze-readiness.v1"
POLICY_ROOT_IDENTITY = "policy.review_input.authorized_root"

_SHA256 = re.compile(SHA256_PATTERN, re.ASCII)
_ZERO_DIGEST = "0" * 64
_PLACEHOLDER_STRINGS = frozenset({"", "NOT_OBSERVED", "NOT_APPLICABLE", "PENDING"})
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "schemas/gate0/config.json"
_SCHEMA_RELATIVE_PATH = "schemas/gate0/config.json"
_MISSING = object()

# The frozen launcher defines the only legitimate sandbox mount shape; the
# config's declared mount lists must agree with it (a mount-policy mismatch is a
# sandbox-boundary mismatch, not a cosmetic difference).
_EXPECTED_RO_MOUNTS = tuple(item["source"] for item in MOUNT_POLICY if item["mode"] == "ro")
_EXPECTED_RW_MOUNTS = tuple(item["source"] for item in MOUNT_POLICY if item["mode"] == "rw")


@dataclass(frozen=True)
class _DigestEntity:
    identity: str
    config_path: tuple[str, ...]
    stage: str
    required_observed: bool = True
    derive: Callable[[], str] | None = None


@dataclass(frozen=True)
class _InputEntity:
    identity: str
    config_path: tuple[str, ...]
    stage: str


# Canonical digest identities and the freeze stage that may legitimately compute
# each one.  Launcher argv/mount-policy digests are locally derivable from the
# frozen launcher templates, so they are verified rather than merely observed.
_DIGEST_ENTITIES = (
    _DigestEntity("corpus.source_manifest_digest", ("corpus", "source_manifest_digest"), "post_inventory"),
    _DigestEntity("model.weights_digest", ("model", "weights_digest"), "model"),
    _DigestEntity("model.processor_digest", ("model", "processor_digest"), "model"),
    _DigestEntity("policy.egress_manifest_digest", ("policy", "egress_manifest_digest"), "policy"),
    _DigestEntity("sandbox.bwrap_digest", ("sandbox", "bwrap_digest"), "sandbox"),
    _DigestEntity("sandbox.interpreter_digest", ("sandbox", "interpreter_digest"), "sandbox"),
    _DigestEntity(
        "sandbox.argv_digest",
        ("sandbox", "argv_digest"),
        "sandbox",
        required_observed=False,
        derive=expected_argv_digest,
    ),
    _DigestEntity(
        "sandbox.mount_policy_digest",
        ("sandbox", "mount_policy_digest"),
        "sandbox",
        required_observed=False,
        derive=expected_mount_policy_digest,
    ),
    _DigestEntity("blinding.blind_mapping_digest", ("blinding", "blind_mapping_digest"), "blinding"),
)

# Non-digest inputs that must not remain placeholder values in a frozen config.
_INPUT_ENTITIES = (
    _InputEntity("corpus.source_root", ("corpus", "source_root"), "pre_inventory"),
    _InputEntity("model.model_identity", ("model", "model_identity"), "model"),
    _InputEntity("model.space_id", ("model", "space_id"), "model"),
    _InputEntity("model.dimension", ("model", "dimension"), "model"),
    _InputEntity("sandbox.bwrap_version", ("sandbox", "bwrap_version"), "sandbox"),
)

_KNOWN_OBSERVED_IDENTITIES = frozenset(entity.identity for entity in _DIGEST_ENTITIES) | {
    POLICY_ROOT_IDENTITY
}

_MISMATCH_CODES = {
    "corpus.source_manifest_digest": "SOURCE_MANIFEST_DIGEST_MISMATCH",
    "policy.egress_manifest_digest": "POLICY_EGRESS_DIGEST_MISMATCH",
    "model.weights_digest": "MODEL_DIGEST_MISMATCH",
    "model.processor_digest": "MODEL_DIGEST_MISMATCH",
    "sandbox.bwrap_digest": "SANDBOX_DIGEST_MISMATCH",
    "sandbox.interpreter_digest": "SANDBOX_DIGEST_MISMATCH",
    "sandbox.argv_digest": "SANDBOX_DIGEST_MISMATCH",
    "sandbox.mount_policy_digest": "SANDBOX_DIGEST_MISMATCH",
    "blinding.blind_mapping_digest": "BLINDING_DIGEST_MISMATCH",
}


def canonical_config_digest(config: Mapping[str, Any]) -> str:
    """Return the exact canonical SHA-256 digest used by the frozen loader."""

    return hashlib.sha256(_config.canonical_json_bytes(_plain(config))).hexdigest()


def inspect_freeze_readiness(
    config: Mapping[str, Any],
    *,
    observed_digests: Mapping[str, Any],
    execution_authorized: bool = False,
) -> Mapping[str, Any]:
    """Return a deterministic preparation-only freeze-readiness audit.

    See the module docstring for the observed-digest key contract and the
    fail-closed semantics.  The supplied ``config`` mapping is never mutated.
    """

    if not isinstance(config, Mapping):
        raise _config.ConfigError("config must be an object")
    if not isinstance(observed_digests, Mapping):
        raise TypeError("observed_digests must be a mapping")
    if not isinstance(execution_authorized, bool):
        raise TypeError("execution_authorized must be a bool")

    plain = _plain(config)
    _validate_against_frozen_schema(plain)

    failures: list[dict[str, str]] = []
    missing_inputs: set[str] = set()

    observations_by_identity, invalid_observations = _collect_observations(observed_digests, failures)

    digest_entries = [
        _inspect_digest_entity(
            entity,
            plain,
            observations_by_identity,
            invalid_observations,
            failures,
            missing_inputs,
        )
        for entity in _DIGEST_ENTITIES
    ]

    for entity in _INPUT_ENTITIES:
        declared = _lookup(plain, entity.config_path)
        if _input_state(declared, entity.identity) != "DECLARED":
            failures.append(
                _failure(
                    "PLACEHOLDER_DECLARED",
                    entity.identity,
                    "declared input is missing or a placeholder value",
                )
            )
            missing_inputs.add(entity.identity)

    digest_entries.append(
        _inspect_policy_root(plain, observations_by_identity, invalid_observations, failures, missing_inputs)
    )
    digest_entries.sort(key=lambda entry: entry["identity"])

    _inspect_mount_lists(plain, failures)

    config_is_placeholder = any(
        entry["declared_state"] not in {"DECLARED", "LOCALLY_DERIVED"} for entry in digest_entries
    ) or any(
        _input_state(_lookup(plain, entity.config_path), entity.identity) != "DECLARED"
        for entity in _INPUT_ENTITIES
    )

    policy_root = _lookup(plain, ("policy", "review_input", "authorized_root"))
    source_root = _lookup(plain, ("corpus", "source_root"))
    configured_roots = (
        {
            "identity": "corpus.source_root",
            "declared": _json_value(source_root),
            "stage": "pre_inventory",
            "opened": False,
        },
        {
            "identity": POLICY_ROOT_IDENTITY,
            "declared": _json_value(policy_root),
            "stage": "policy",
            "opened": False,
        },
    )

    failures.sort(key=lambda item: (item["code"], item["identity"], item["detail"]))
    status = "BLOCKED_PREREQUISITE" if failures else "READY_FOR_FREEZE_REVIEW"

    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "freeze_state": "NOT_FROZEN",
        "preparation_only": True,
        "authentic": False,
        "approval": "NOT_GRANTED",
        "gate_verdict": "NOT_RUN",
        "execution_authorized": execution_authorized,
        "execution_activation": "NOT_AVAILABLE_IN_D1_SOFTWARE",
        "config_digest": canonical_config_digest(plain),
        "config_is_placeholder": config_is_placeholder,
        "digest_entries": digest_entries,
        "failures": failures,
        "missing_inputs": sorted(missing_inputs),
        "provenance": {
            "inspector": "gate0.config_freeze.inspect_freeze_readiness",
            "observed_digest_source": "caller_supplied_metadata",
            "observed_digest_authenticity": "UNVERIFIED",
            "schema_validation": "gate0.config loader schema/invariant validators (read-only)",
            "dependency_lock_validation": "NOT_VALIDATED_CONFIG_ONLY",
            "readiness_scope": "configuration-metadata-only",
            "filesystem_reads": [_SCHEMA_RELATIVE_PATH],
            "configured_roots": list(configured_roots),
            "model_assets_opened": False,
            "network_used": False,
            "d2_inputs": "NOT_OBSERVED",
            "d3_execution_authorization": "NOT_GRANTED",
        },
    }


# ---------------------------------------------------------------------------
# Validation / normalization helpers
# ---------------------------------------------------------------------------


def _validate_against_frozen_schema(config: dict[str, Any]) -> None:
    """Validate with the frozen loader's own validators (read-only)."""

    try:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:  # pragma: no cover - environment failure
        raise _config.ConfigError(f"config schema missing: {_SCHEMA_PATH}") from exc
    _config._validate_schema(config, schema)
    _config._validate(config)


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _lookup(config: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = config
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return _MISSING
        node = node[key]
    return node


def _json_value(value: Any) -> Any:
    return None if value is _MISSING else value


def _digest_state(value: Any) -> str:
    if value is _MISSING or value is None:
        return "MISSING"
    if not isinstance(value, str):
        return "INVALID"
    if value != value.strip() or value in _PLACEHOLDER_STRINGS:
        return "PLACEHOLDER_NOT_OBSERVED"
    if _SHA256.fullmatch(value) is None:
        return "INVALID"
    if value == _ZERO_DIGEST:
        return "PLACEHOLDER_ZERO"
    return "DECLARED"


def _input_state(value: Any, identity: str) -> str:
    if value is _MISSING or value is None:
        return "MISSING"
    if identity.endswith(".dimension"):
        return "DECLARED" if isinstance(value, int) and not isinstance(value, bool) and value > 0 else "PLACEHOLDER"
    if isinstance(value, str):
        if value.strip() in _PLACEHOLDER_STRINGS:
            return "PLACEHOLDER"
        if identity == "corpus.source_root":
            # A template-relative generic root is not a concrete authorized
            # corpus location; require an absolute declared path.
            return "DECLARED" if value == value.strip() and os.path.isabs(value) else "PLACEHOLDER"
        return "DECLARED"
    return "DECLARED"


def _is_valid_observed_digest(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None and value != _ZERO_DIGEST


def _failure(code: str, identity: str, detail: str) -> dict[str, str]:
    return {"code": code, "identity": identity, "detail": detail}


# ---------------------------------------------------------------------------
# Observed-digest collection
# ---------------------------------------------------------------------------


def _collect_observations(
    observed_digests: Mapping[Any, Any],
    failures: list[dict[str, str]],
) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    raw: dict[str, list[tuple[str, Any, str]]] = {}
    for raw_key in sorted(observed_digests, key=str):
        key = str(raw_key)
        stage, separator, identity = key.partition(":")
        if (
            not isinstance(raw_key, str)
            or not separator
            or not stage
            or not identity
            or ":" in identity
            or identity not in _KNOWN_OBSERVED_IDENTITIES
        ):
            failures.append(
                _failure(
                    "UNKNOWN_OBSERVED_KEY",
                    key,
                    "observed keys must be '<stage>:<known digest identity>'",
                )
            )
            continue
        raw.setdefault(identity, []).append((stage, observed_digests[raw_key], key))

    accepted: dict[str, dict[str, str]] = {}
    invalid: dict[str, Any] = {}
    for identity, items in raw.items():
        valid = [(stage, value) for stage, value, _key in items if _is_valid_observed_digest(value)]
        for _stage, value, _key in items:
            if not _is_valid_observed_digest(value):
                failures.append(
                    _failure(
                        "OBSERVED_DIGEST_INVALID",
                        identity,
                        "observed digest is not a non-zero lowercase SHA-256 hex value",
                    )
                )
                invalid.setdefault(identity, value)
        if len(items) > 1:
            failures.append(
                _failure(
                    "AMBIGUOUS_FREEZE_POINT",
                    identity,
                    "multiple freeze-point observations exist for one identity",
                )
            )
        elif len(valid) == 1:
            accepted[identity] = {"stage": valid[0][0], "value": valid[0][1]}
    return accepted, invalid


# ---------------------------------------------------------------------------
# Per-identity inspection
# ---------------------------------------------------------------------------


def _inspect_digest_entity(
    entity: _DigestEntity,
    config: Mapping[str, Any],
    observations: Mapping[str, Mapping[str, str]],
    invalid_observations: Mapping[str, Any],
    failures: list[dict[str, str]],
    missing_inputs: set[str],
) -> dict[str, Any]:
    declared = _lookup(config, entity.config_path)
    declared_state = _digest_state(declared)
    observed = observations.get(entity.identity)
    invalid_value = invalid_observations.get(entity.identity, _MISSING) if observed is None else _MISSING
    observed_supplied = observed is not None or entity.identity in invalid_observations
    derived_digest = entity.derive() if entity.derive is not None else None

    verification = "UNKNOWN"
    if entity.derive is not None:
        verification = _inspect_derived_entity(
            entity,
            declared,
            declared_state,
            observed,
            invalid_value,
            derived_digest,
            failures,
        )
        if declared_state != "DECLARED":
            _add_declared_failure(entity.identity, declared_state, failures)
            missing_inputs.add(entity.identity)
            verification = "INVALID" if declared_state == "INVALID" else "PLACEHOLDER"
    elif declared_state != "DECLARED":
        _add_declared_failure(entity.identity, declared_state, failures)
        missing_inputs.add(entity.identity)
        verification = "PLACEHOLDER" if declared_state != "INVALID" else "INVALID"
    elif observed is None and observed_supplied:
        # A supplied-but-invalid observation is a tampering/format failure, not
        # an absent digest; keep the provenance and do not misreport it.
        missing_inputs.add(entity.identity)
        verification = "INVALID_OBSERVED"
    elif observed is None:
        failures.append(
            _failure(
                "MISSING_OBSERVED",
                entity.identity,
                "no observed digest supplied for the declared final digest",
            )
        )
        missing_inputs.add(entity.identity)
        verification = "MISSING_OBSERVED"
    elif observed["stage"] != entity.stage:
        failures.append(
            _failure(
                "STAGE_MISMATCH",
                entity.identity,
                f"digest may only be observed at stage {entity.stage}",
            )
        )
        verification = "MISMATCH"
    elif observed["value"] != declared:
        failures.append(
            _failure(
                _MISMATCH_CODES.get(entity.identity, "OBSERVED_DIGEST_MISMATCH"),
                entity.identity,
                "observed digest does not match the declared frozen digest",
            )
        )
        verification = "MISMATCH"
    else:
        verification = "MATCHED"

    return {
        "identity": entity.identity,
        "config_path": ".".join(entity.config_path),
        "stage": entity.stage,
        "required_observed": entity.required_observed,
        "locally_derived": entity.derive is not None,
        "derived_digest": derived_digest,
        "declared": _json_value(declared),
        "declared_state": declared_state,
        "observed": observed["value"] if observed is not None else (
            None if invalid_value is _MISSING else invalid_value
        ),
        "observed_stage": observed["stage"] if observed is not None else None,
        "observed_supplied": observed_supplied,
        "observed_source": "caller_supplied_metadata" if observed_supplied else None,
        "observed_authenticity": "UNVERIFIED" if observed_supplied else None,
        "verification": verification,
    }


def _inspect_derived_entity(
    entity: _DigestEntity,
    declared: Any,
    declared_state: str,
    observed: Mapping[str, str] | None,
    invalid_value: Any,
    derived_digest: str | None,
    failures: list[dict[str, str]],
) -> str:
    verification = "LOCALLY_DERIVED"
    if declared_state == "DECLARED" and declared != derived_digest:
        failures.append(
            _failure(
                _MISMATCH_CODES.get(entity.identity, "OBSERVED_DIGEST_MISMATCH"),
                entity.identity,
                "declared digest does not match the locally derived canonical digest",
            )
        )
        verification = "LOCALLY_DERIVED_MISMATCH"
    if observed is not None:
        if observed["stage"] != entity.stage:
            failures.append(
                _failure(
                    "STAGE_MISMATCH",
                    entity.identity,
                    f"digest may only be observed at stage {entity.stage}",
                )
            )
            verification = "MISMATCH"
        elif declared_state == "DECLARED" and observed["value"] != declared:
            failures.append(
                _failure(
                    _MISMATCH_CODES.get(entity.identity, "OBSERVED_DIGEST_MISMATCH"),
                    entity.identity,
                    "observed digest does not match the declared frozen digest",
                )
            )
            verification = "MISMATCH"
    elif invalid_value is not _MISSING and declared_state == "DECLARED":
        verification = "INVALID_OBSERVED"
    return verification


def _add_declared_failure(
    identity: str,
    declared_state: str,
    failures: list[dict[str, str]],
) -> None:
    if declared_state == "INVALID":
        failures.append(
            _failure(
                "INVALID_DECLARED_DIGEST",
                identity,
                "declared digest is not a lowercase SHA-256 hex value",
            )
        )
    else:
        failures.append(
            _failure(
                "PLACEHOLDER_DECLARED",
                identity,
                "declared digest is missing or a placeholder value",
            )
        )


def _inspect_policy_root(
    config: Mapping[str, Any],
    observations: Mapping[str, Mapping[str, str]],
    invalid_observations: Mapping[str, Any],
    failures: list[dict[str, str]],
    missing_inputs: set[str],
) -> dict[str, Any]:
    """Inspect the policy review-root identity (a derived digest, not a config digest).

    The observation is required: reporting the declared root without proving the
    caller's rooted identity would leave a silent gap in the fail-closed
    contract.
    """

    root = _lookup(config, ("policy", "review_input", "authorized_root"))
    root_state = _input_state(root, POLICY_ROOT_IDENTITY)
    observed = observations.get(POLICY_ROOT_IDENTITY)
    invalid_value = invalid_observations.get(POLICY_ROOT_IDENTITY) if observed is None else None
    observed_supplied = observed is not None or POLICY_ROOT_IDENTITY in invalid_observations
    derived: str | None = None

    if root_state != "DECLARED":
        failures.append(
            _failure(
                "PLACEHOLDER_DECLARED",
                POLICY_ROOT_IDENTITY,
                "declared policy review root is missing or a placeholder value",
            )
        )
        missing_inputs.add(POLICY_ROOT_IDENTITY)
        verification = "PLACEHOLDER" if root_state != "INVALID" else "INVALID"
    else:
        derived = digest_bytes(str(root).encode("utf-8"))
        if observed is not None:
            if observed["stage"] != "policy":
                failures.append(
                    _failure(
                        "STAGE_MISMATCH",
                        POLICY_ROOT_IDENTITY,
                        "policy root identity may only be observed at stage policy",
                    )
                )
                verification = "MISMATCH"
            elif observed["value"] != derived:
                failures.append(
                    _failure(
                        "POLICY_ROOT_MISMATCH",
                        POLICY_ROOT_IDENTITY,
                        "observed policy root identity does not match the declared review root",
                    )
                )
                verification = "MISMATCH"
            else:
                verification = "MATCHED"
        elif observed_supplied:
            missing_inputs.add(POLICY_ROOT_IDENTITY)
            verification = "INVALID_OBSERVED"
        else:
            failures.append(
                _failure(
                    "MISSING_OBSERVED",
                    POLICY_ROOT_IDENTITY,
                    "no observed identity supplied for the declared policy review root",
                )
            )
            missing_inputs.add(POLICY_ROOT_IDENTITY)
            verification = "MISSING_OBSERVED"

    return {
        "identity": POLICY_ROOT_IDENTITY,
        "config_path": "policy.review_input.authorized_root",
        "stage": "policy",
        "required_observed": True,
        "locally_derived": True,
        "derived_digest": derived,
        "declared": _json_value(root),
        "declared_state": root_state,
        "observed": observed["value"] if observed is not None else invalid_value,
        "observed_stage": observed["stage"] if observed is not None else None,
        "observed_supplied": observed_supplied,
        "observed_source": "caller_supplied_metadata" if observed_supplied else None,
        "observed_authenticity": "UNVERIFIED" if observed_supplied else None,
        "verification": verification,
    }


def _inspect_mount_lists(config: Mapping[str, Any], failures: list[dict[str, str]]) -> None:
    """Refuse a config whose declared mount lists disagree with the frozen launcher."""

    declared_ro = _lookup(config, ("sandbox", "read_only_mounts"))
    declared_rw = _lookup(config, ("sandbox", "writable_mounts"))

    def _as_tuple(value: Any) -> tuple[Any, ...] | None:
        if isinstance(value, (list, tuple)):
            return tuple(value)
        return None

    if _as_tuple(declared_ro) != _EXPECTED_RO_MOUNTS:
        failures.append(
            _failure(
                "MOUNT_POLICY_MISMATCH",
                "sandbox.read_only_mounts",
                "declared read-only mounts do not match the frozen launcher mount policy",
            )
        )
    if _as_tuple(declared_rw) != _EXPECTED_RW_MOUNTS:
        failures.append(
            _failure(
                "MOUNT_POLICY_MISMATCH",
                "sandbox.writable_mounts",
                "declared writable mounts do not match the frozen launcher mount policy",
            )
        )
