import copy
import json
from pathlib import Path

import pytest

from gate0.config import ConfigError, canonical_json_bytes, load_config
from gate0.launcher_attestation import expected_argv_digest, expected_mount_policy_digest
from gate0.launcher_attestation import ARGV_TEMPLATE, normalize_actual_argv


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "config/gate0/default.json"
LOCK = ROOT / "requirements/gate0.lock"


def test_default_config_emits_stable_digests_and_immutable_profile():
    result = load_config(CONFIG, lock_path=LOCK)
    golden = json.loads((ROOT / "tests/gate0/fixtures/golden/config.json").read_text())
    assert len(result.config_digest) == 64
    assert result.config_digest == golden["config_digest"]
    assert len(result.dependency_lock_digest) == 64
    assert result.python_version == "3.11.9"
    assert result.config["policy"]["gate_owner_id"] == "gate0-owner"
    assert result.config["policy"]["review_input"]["authorized_root"]
    assert result.config["windows"]["duration_seconds"] == 4
    with pytest.raises(TypeError):
        result.config["windows"]["duration_seconds"] = 5


def test_sandbox_attestation_digest_fields_are_config_bound(tmp_path):
    result = load_config(CONFIG, lock_path=LOCK)
    sandbox = result.config["sandbox"]
    assert sandbox["argv_digest"] == expected_argv_digest()
    assert sandbox["mount_policy_digest"] == expected_mount_policy_digest()

    data = json.loads(CONFIG.read_text())
    del data["sandbox"]["argv_digest"]
    path = tmp_path / "config-missing-argv-digest.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match="required field"):
        load_config(path, lock_path=LOCK)


def test_canonical_sandbox_config_matches_literal_launcher_contract():
    config = json.loads(CONFIG.read_text())
    assert config["sandbox"]["bwrap_path"] == "/usr/bin/bwrap"
    assert config["sandbox"]["read_only_mounts"] == [
        "REPO_ROOT", "INPUT_ROOT", "/usr", "/lib", "/lib64", "/etc/ld.so.cache"
    ]
    assert config["sandbox"]["writable_mounts"] == ["OUTPUT_ROOT"]


def test_launcher_normalization_rejects_run_value_in_wrong_structural_slot():
    context = {"repo_root": "/repo", "input_root": "/input", "output_root": "/output",
               "run_id": "run-1", "run_dir": "/run", "stage": "preflight"}
    dynamic = {"REPO_ROOT": "/repo", "INPUT_ROOT": "/input", "OUTPUT_ROOT": "/output",
               "RUN_ID": "run-1", "RUN_DIR": "/run", "STAGE": "preflight",
               "REPO_ROOT/src": "/repo/src", "ATTESTATION_JSON": "{}"}
    actual = [dynamic.get(value, value) for value in ARGV_TEMPLATE]
    actual[1] = "preflight"
    with pytest.raises(ValueError, match="SANDBOX_ATTESTATION"):
        normalize_actual_argv(actual, context)


def test_unknown_nested_field_is_rejected(tmp_path):
    data = json.loads(CONFIG.read_text())
    data["sampling"]["unexpected"] = True
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match="unknown field"):
        load_config(path, lock_path=LOCK)


def test_required_and_invariant_fields_are_rejected(tmp_path):
    data = json.loads(CONFIG.read_text())
    del data["thresholds"]["paired_lift_den"]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match="required field"):
        load_config(path, lock_path=LOCK)

    data = json.loads(CONFIG.read_text())
    data["sampling"]["target_ticks"] = [0, 1]
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match="target_ticks"):
        load_config(path, lock_path=LOCK)


def test_schema_round_trip_matches_config_shape():
    schema = json.loads((ROOT / "schemas/gate0/config.json").read_text())
    config = json.loads(CONFIG.read_text())
    assert set(schema["properties"]) == set(config)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["retention"]["propertyNames"]["enum"] == [
        "SOURCE_REFERENCE", "DERIVED_REPLAYABLE", "DERIVED_RESTRICTED",
        "AUDIT_MINIMUM", "TOMBSTONE"
    ]


def test_missing_lock_is_rejected(tmp_path):
    with pytest.raises(ConfigError, match="lock"):
        load_config(CONFIG, lock_path=tmp_path / "missing.lock")


def test_nested_schema_enum_is_enforced(tmp_path):
    data = json.loads(CONFIG.read_text())
    data["policy"]["provider_model_boundary"] = "remote"
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match="schema enum"):
        load_config(path, lock_path=LOCK)
