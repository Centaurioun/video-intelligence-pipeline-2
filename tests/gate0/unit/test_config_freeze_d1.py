"""D-1 synthetic tests for the P-09 configuration-freeze readiness inspector.

Chronological RED/GREEN discipline (Gate-0 D-1, Lane C).  The inspector is a
*preparation-only* audit tool: it never freezes a configuration, never certifies
authenticity, never opens a configured root or model asset, and never turns the
``execution_authorized`` flag into a trust grant.  All metadata used here is
generated/synthetic; no corpus media, model weights, network or D-2/D-3 input is
touched.

Observed-digest key grammar (documented contract under test)::

    "<stage>:<identity>"

where ``stage`` is the freeze stage at which the digest may legitimately be
computed (``pre_inventory``, ``post_inventory``, ``model``, ``policy``,
``sandbox``, ``blinding``) and ``identity`` is one of the canonical digest
identities reported by the inspector.  Every observed value is caller-supplied
metadata of unverified authenticity.
"""

from __future__ import annotations

import builtins
import copy
import hashlib
import io
import json
import os
import random
from pathlib import Path

import pytest

from gate0.config import ConfigError, canonical_json_bytes, load_config
from gate0.config_freeze import inspect_freeze_readiness
from gate0.identity import digest_bytes, digest_json

ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT / "config/gate0/default.json"
LOCK_PATH = ROOT / "requirements/gate0.lock"

SENTINEL_INPUT_ROOT = "/synthetic-input-root-that-must-not-be-opened"
REQUIRED_OBSERVED_IDENTITIES = (
    "corpus.source_manifest_digest",
    "model.weights_digest",
    "model.processor_digest",
    "policy.egress_manifest_digest",
    "sandbox.bwrap_digest",
    "sandbox.interpreter_digest",
    "blinding.blind_mapping_digest",
)
PLACEHOLDER_IDENTITIES = REQUIRED_OBSERVED_IDENTITIES + (
    "corpus.source_root",
    "model.model_identity",
    "model.space_id",
    "model.dimension",
    "sandbox.bwrap_version",
)


def _default_config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def _synthetic_digest(label: str) -> str:
    """Deterministic generated metadata digest; never a real asset identity."""

    return digest_json({"synthetic_metadata": label})


def _synthetic_ready_config() -> dict:
    """Derive a non-placeholder *synthetic* config from the frozen default.

    Only the D-2/D-3-dependent placeholder values are substituted with clearly
    generated metadata.  Frozen windows/sampling/thresholds/counts are copied
    unchanged from the frozen default config.
    """

    config = _default_config()
    config["corpus"]["source_root"] = SENTINEL_INPUT_ROOT
    config["corpus"]["source_manifest_digest"] = _synthetic_digest("source-manifest-rev-1")
    config["model"].update(
        {
            "model_identity": "synthetic-local-model-identity",
            "weights_digest": _synthetic_digest("weights"),
            "processor_digest": _synthetic_digest("processor"),
            "space_id": "synthetic-embedding-space",
            "dimension": 64,
        }
    )
    config["policy"]["egress_manifest_digest"] = _synthetic_digest("egress-manifest")
    config["sandbox"].update(
        {
            "bwrap_version": "synthetic-bwrap-1.0",
            "bwrap_digest": _synthetic_digest("bwrap"),
            "interpreter_digest": _synthetic_digest("interpreter"),
        }
    )
    config["blinding"]["blind_mapping_digest"] = _synthetic_digest("blind-mapping")
    return config


def _observed_for(config: dict) -> dict[str, str]:
    return {
        "post_inventory:corpus.source_manifest_digest": config["corpus"]["source_manifest_digest"],
        "model:model.weights_digest": config["model"]["weights_digest"],
        "model:model.processor_digest": config["model"]["processor_digest"],
        "policy:policy.egress_manifest_digest": config["policy"]["egress_manifest_digest"],
        "sandbox:sandbox.bwrap_digest": config["sandbox"]["bwrap_digest"],
        "sandbox:sandbox.interpreter_digest": config["sandbox"]["interpreter_digest"],
        "blinding:blinding.blind_mapping_digest": config["blinding"]["blind_mapping_digest"],
        "policy:policy.review_input.authorized_root": digest_bytes(
            config["policy"]["review_input"]["authorized_root"].encode("utf-8")
        ),
    }


def _codes(report: dict) -> set[str]:
    return {failure["code"] for failure in report["failures"]}


def _failure_identities(report: dict) -> set[str]:
    return {failure["identity"] for failure in report["failures"]}


def _entry(report: dict, identity: str) -> dict:
    entries = {entry["identity"]: entry for entry in report["digest_entries"]}
    return entries[identity]


# ---------------------------------------------------------------------------
# C1 — placeholder config cannot be frozen as real
# ---------------------------------------------------------------------------


def test_placeholder_config_cannot_be_frozen_as_real() -> None:
    loaded = load_config(CONFIG_PATH, LOCK_PATH)
    report = inspect_freeze_readiness(loaded.config, observed_digests={})

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert report["freeze_state"] == "NOT_FROZEN"
    assert report["authentic"] is False
    assert report["preparation_only"] is True
    assert report["gate_verdict"] == "NOT_RUN"
    assert report["config_is_placeholder"] is True
    # The canonical digest is still the exact frozen-loader digest, so the
    # placeholder state is reported rather than silently re-digested.
    assert report["config_digest"] == loaded.config_digest
    assert "PLACEHOLDER_DECLARED" in _codes(report)
    assert set(PLACEHOLDER_IDENTITIES) <= set(report["missing_inputs"])
    assert set(PLACEHOLDER_IDENTITIES) <= _failure_identities(report)


def test_placeholder_cannot_be_repaired_by_observation() -> None:
    config = _default_config()
    observed = {
        "model:model.weights_digest": _synthetic_digest("weights"),
        "model:model.processor_digest": _synthetic_digest("processor"),
        "post_inventory:corpus.source_manifest_digest": _synthetic_digest("manifest"),
    }
    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "PLACEHOLDER_DECLARED" in _codes(report)
    for identity in observed:
        assert _entry(report, identity.split(":", 1)[1])["declared_state"] != "DECLARED"
    assert report["freeze_state"] == "NOT_FROZEN"


def test_generated_fixture_freeze_is_not_authentic() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "READY_FOR_FREEZE_REVIEW"
    assert report["failures"] == []
    assert report["missing_inputs"] == []
    assert report["config_is_placeholder"] is False
    # A clean synthetic inspection is still not an authentic frozen config and
    # carries no Gate verdict or signed/approved status.
    assert report["authentic"] is False
    assert report["preparation_only"] is True
    assert report["freeze_state"] == "NOT_FROZEN"
    assert report["gate_verdict"] == "NOT_RUN"
    assert report["execution_activation"] == "NOT_AVAILABLE_IN_D1_SOFTWARE"
    assert report["schema_version"] == "gate0.config-freeze-readiness.v1"

    expected_digest = hashlib.sha256(canonical_json_bytes(config)).hexdigest()
    assert report["config_digest"] == expected_digest


def test_generated_fixture_freeze_audit_is_deterministic() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    first = inspect_freeze_readiness(config, observed_digests=observed)
    expected_bytes = canonical_json_bytes(first)

    items = list(observed.items())
    rng = random.Random(20261025)
    for _ in range(25):
        rng.shuffle(items)
        candidate = inspect_freeze_readiness(copy.deepcopy(config), observed_digests=dict(items))
        assert canonical_json_bytes(candidate) == expected_bytes

    assert [entry["identity"] for entry in first["digest_entries"]] == sorted(
        entry["identity"] for entry in first["digest_entries"]
    )
    assert first["failures"] == []
    assert first["missing_inputs"] == []


def test_execution_authorized_flag_is_not_a_trust_grant() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    plain = inspect_freeze_readiness(config, observed_digests=observed, execution_authorized=False)
    claimed = inspect_freeze_readiness(config, observed_digests=observed, execution_authorized=True)

    assert claimed["execution_authorized"] is True
    assert claimed["status"] == plain["status"] == "READY_FOR_FREEZE_REVIEW"
    assert claimed["execution_activation"] == "NOT_AVAILABLE_IN_D1_SOFTWARE"
    assert claimed["authentic"] is False
    assert claimed["preparation_only"] is True
    assert claimed["gate_verdict"] == "NOT_RUN"
    assert claimed["freeze_state"] == "NOT_FROZEN"
    assert {key: value for key, value in claimed.items() if key != "execution_authorized"} == {
        key: value for key, value in plain.items() if key != "execution_authorized"
    }


def test_schema_validation_is_pinned_to_the_frozen_loader() -> None:
    config = _synthetic_ready_config()
    config["model"]["unexpected_extra_field"] = "x"
    with pytest.raises(ConfigError, match=r"unknown field"):
        inspect_freeze_readiness(config, observed_digests={})

    # Reuses the frozen loader's own invariant, not a duplicated copy.
    config = _synthetic_ready_config()
    config["model"]["processor_digest"] = "a" * 63
    with pytest.raises(ConfigError, match="digest field must be SHA-256"):
        inspect_freeze_readiness(config, observed_digests={})

    config = _synthetic_ready_config()
    config["thresholds"]["semantic_hit_at_10_num"] = 19
    with pytest.raises(ConfigError, match="schema invariant"):
        inspect_freeze_readiness(config, observed_digests={})


# ---------------------------------------------------------------------------
# C2 — mutation / substitution / tampering / ambiguity fail closed
# ---------------------------------------------------------------------------


def test_digest_substitution_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    config["model"]["processor_digest"] = _synthetic_digest("substituted-processor")

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "MODEL_DIGEST_MISMATCH" in _codes(report)
    assert "model.processor_digest" in _failure_identities(report)
    assert _entry(report, "model.processor_digest")["verification"] == "MISMATCH"


def test_misreported_policy_root_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    observed["policy:policy.review_input.authorized_root"] = digest_bytes(b"/somewhere-else/review-input")

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "POLICY_ROOT_MISMATCH" in _codes(report)
    assert "policy.review_input.authorized_root" in _failure_identities(report)


def test_source_manifest_revision_mismatch_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    # The same identity resolved against a different source-manifest revision.
    observed["post_inventory:corpus.source_manifest_digest"] = digest_json(
        {"synthetic_metadata": "source-manifest-rev-2"}
    )

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "SOURCE_MANIFEST_DIGEST_MISMATCH" in _codes(report)
    assert "corpus.source_manifest_digest" in _failure_identities(report)


def test_ambiguous_pre_post_inventory_freeze_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    observed["pre_inventory:corpus.source_manifest_digest"] = _synthetic_digest("pre-inventory-manifest")

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "AMBIGUOUS_FREEZE_POINT" in _codes(report)
    assert "corpus.source_manifest_digest" in _failure_identities(report)


def test_source_manifest_cannot_be_observed_before_inventory() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    del observed["post_inventory:corpus.source_manifest_digest"]
    observed["pre_inventory:corpus.source_manifest_digest"] = config["corpus"]["source_manifest_digest"]

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "STAGE_MISMATCH" in _codes(report)
    assert "corpus.source_manifest_digest" in _failure_identities(report)


@pytest.mark.parametrize(
    "tampered",
    [
        "0" * 64,
        _synthetic_digest("valid").upper(),
        _synthetic_digest("valid")[:-1],
        "g" * 64,
        "",
        None,
        123,
    ],
)
def test_digest_tampering_fails_closed(tampered: object) -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    observed["model:model.processor_digest"] = tampered  # type: ignore[assignment]

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "OBSERVED_DIGEST_INVALID" in _codes(report)
    # A supplied-but-invalid observation must not be re-diagnosed as "absent".
    assert "MISSING_OBSERVED" not in _codes(report)
    entry = _entry(report, "model.processor_digest")
    assert entry["observed_supplied"] is True
    assert entry["verification"] == "INVALID_OBSERVED"
    assert report["authentic"] is False


def test_unknown_observed_keys_fail_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    observed["sandbox:sandbox.unknown_digest"] = _synthetic_digest("unknown")
    observed["model.model.processor_digest"] = _synthetic_digest("unqualified")
    observed["model:model.processor_digest:extra"] = _synthetic_digest("extra-scope")

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert _codes(report) == {"UNKNOWN_OBSERVED_KEY"}
    assert report["failures"] == sorted(report["failures"], key=lambda item: (item["code"], item["identity"], item["detail"]))


def test_wrong_stage_observation_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    del observed["post_inventory:corpus.source_manifest_digest"]
    observed["model:corpus.source_manifest_digest"] = config["corpus"]["source_manifest_digest"]

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "STAGE_MISMATCH" in _codes(report)


def test_missing_observation_for_final_declared_digest_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    del observed["model:model.weights_digest"]

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "MISSING_OBSERVED" in _codes(report)
    assert "model.weights_digest" in report["missing_inputs"]
    assert _entry(report, "model.weights_digest")["verification"] == "MISSING_OBSERVED"


def test_locally_derived_sandbox_digests_are_checked() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    config["sandbox"]["argv_digest"] = _synthetic_digest("mutated-argv")
    config["sandbox"]["mount_policy_digest"] = _synthetic_digest("mutated-mount-policy")

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert _codes(report) == {"SANDBOX_DIGEST_MISMATCH"}
    assert {"sandbox.argv_digest", "sandbox.mount_policy_digest"} <= _failure_identities(report)


# ---------------------------------------------------------------------------
# Provenance, stage reporting, no I/O on configured roots / model assets
# ---------------------------------------------------------------------------


def test_observed_digest_sources_and_stages_are_reported() -> None:
    config = _synthetic_ready_config()
    report = inspect_freeze_readiness(config, observed_digests=_observed_for(config))

    expected_stages = {
        "corpus.source_manifest_digest": "post_inventory",
        "model.weights_digest": "model",
        "model.processor_digest": "model",
        "policy.egress_manifest_digest": "policy",
        "policy.review_input.authorized_root": "policy",
        "sandbox.bwrap_digest": "sandbox",
        "sandbox.interpreter_digest": "sandbox",
        "blinding.blind_mapping_digest": "blinding",
        "sandbox.argv_digest": "sandbox",
        "sandbox.mount_policy_digest": "sandbox",
    }
    for identity, stage in expected_stages.items():
        entry = _entry(report, identity)
        assert entry["stage"] == stage
        assert isinstance(entry["config_path"], str)
        if identity in ("sandbox.argv_digest", "sandbox.mount_policy_digest"):
            # Locally derived identities are verified, not merely observed.
            assert entry["observed_supplied"] is False
            assert entry["locally_derived"] is True
        else:
            assert entry["observed_supplied"] is True
        if entry["observed"] is not None:
            assert entry["observed_source"] == "caller_supplied_metadata"
            assert entry["observed_authenticity"] == "UNVERIFIED"

    provenance = report["provenance"]
    assert provenance["observed_digest_authenticity"] == "UNVERIFIED"
    assert provenance["model_assets_opened"] is False
    assert provenance["network_used"] is False
    assert provenance["dependency_lock_validation"] == "NOT_VALIDATED_CONFIG_ONLY"
    roots = {item["identity"]: item for item in provenance["configured_roots"]}
    assert roots["corpus.source_root"]["declared"] == SENTINEL_INPUT_ROOT
    assert all(item["opened"] is False for item in provenance["configured_roots"])


def test_configured_roots_and_model_assets_are_never_opened(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)

    def _is_forbidden(path: object) -> bool:
        if not isinstance(path, (str, bytes, os.PathLike)):
            return False
        text = os.fspath(path)
        text = text.decode() if isinstance(text, bytes) else text
        return bool(
            isinstance(text, str)
            and (
                SENTINEL_INPUT_ROOT in text
                or "review-input" in text
                or "model" in Path(text).name.lower()
            )
        )

    def _guard(real):
        def guarded(path, *args, **kwargs):
            if _is_forbidden(path):
                raise AssertionError(f"configured root/model asset opened: {path!r}")
            return real(path, *args, **kwargs)

        return guarded

    # Positive control: the guard really can fire (so a silent no-op patch would
    # not masquerade as evidence).
    with pytest.raises(AssertionError, match="configured root/model asset opened"):
        _guard(lambda *args, **kwargs: None)(SENTINEL_INPUT_ROOT)

    monkeypatch.setattr(builtins, "open", _guard(builtins.open))
    monkeypatch.setattr(io, "open", _guard(io.open))
    monkeypatch.setattr(os, "open", _guard(os.open))
    monkeypatch.setattr(os, "listdir", _guard(os.listdir))
    monkeypatch.setattr(os, "scandir", _guard(os.scandir))
    monkeypatch.setattr(Path, "stat", _guard(Path.stat))
    monkeypatch.setattr(Path, "exists", _guard(Path.exists))
    monkeypatch.setattr(Path, "iterdir", _guard(Path.iterdir))

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "READY_FOR_FREEZE_REVIEW"
    assert report["provenance"]["model_assets_opened"] is False


def test_relative_template_source_root_cannot_be_ready() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    # The frozen template value "inputs" is not a concrete authorized root.
    config["corpus"]["source_root"] = "inputs"

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "PLACEHOLDER_DECLARED" in _codes(report)
    assert "corpus.source_root" in report["missing_inputs"]
    assert report["config_is_placeholder"] is True


def test_missing_policy_root_observation_fails_closed() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    del observed["policy:policy.review_input.authorized_root"]

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert _codes(report) == {"MISSING_OBSERVED"}
    assert "policy.review_input.authorized_root" in report["missing_inputs"]
    entry = _entry(report, "policy.review_input.authorized_root")
    assert entry["observed_supplied"] is False
    assert entry["verification"] == "MISSING_OBSERVED"
    assert entry["locally_derived"] is True


def test_placeholder_policy_root_sets_placeholder_flag() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    config["policy"]["review_input"]["authorized_root"] = "   "

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "PLACEHOLDER_DECLARED" in _codes(report)
    assert "policy.review_input.authorized_root" in _failure_identities(report)
    assert report["config_is_placeholder"] is True
    entry = _entry(report, "policy.review_input.authorized_root")
    assert entry["declared_state"] != "DECLARED"
    assert entry["observed_supplied"] is True


def test_invalid_observed_digest_on_derived_identity_keeps_provenance() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    observed["sandbox:sandbox.argv_digest"] = "not-a-digest"

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "OBSERVED_DIGEST_INVALID" in _codes(report)
    assert "MISSING_OBSERVED" not in _codes(report)
    entry = _entry(report, "sandbox.argv_digest")
    assert entry["observed_supplied"] is True
    assert entry["verification"] == "INVALID_OBSERVED"


def test_mount_lists_must_match_the_frozen_launcher_policy() -> None:
    config = _synthetic_ready_config()
    observed = _observed_for(config)
    config["sandbox"]["read_only_mounts"].append("/etc")

    report = inspect_freeze_readiness(config, observed_digests=observed)

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "MOUNT_POLICY_MISMATCH" in _codes(report)

    config = _synthetic_ready_config()
    config["sandbox"]["writable_mounts"].append("/tmp")
    report = inspect_freeze_readiness(config, observed_digests=_observed_for(config))

    assert report["status"] == "BLOCKED_PREREQUISITE"
    assert "MOUNT_POLICY_MISMATCH" in _codes(report)


def test_non_bool_execution_authorized_is_rejected() -> None:
    config = _synthetic_ready_config()
    with pytest.raises(TypeError, match="execution_authorized must be a bool"):
        inspect_freeze_readiness(
            config,
            observed_digests=_observed_for(config),
            execution_authorized="false",  # type: ignore[arg-type]
        )


def test_non_mapping_inputs_are_rejected() -> None:
    config = _synthetic_ready_config()
    with pytest.raises(ConfigError, match="config must be an object"):
        inspect_freeze_readiness([], observed_digests={})  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="observed_digests must be a mapping"):
        inspect_freeze_readiness(config, observed_digests=[])  # type: ignore[arg-type]


def test_inspection_does_not_mutate_the_frozen_config() -> None:
    config = _synthetic_ready_config()
    before = copy.deepcopy(config)
    inspect_freeze_readiness(config, observed_digests=_observed_for(config))

    assert config == before
    # Frozen thresholds / window cardinality remain untouched by the tool.
    assert config["thresholds"] == before["thresholds"]
    assert config["sampling"]["target_ticks"] == before["sampling"]["target_ticks"]
    assert config["windows"]["duration_seconds"] == 4
