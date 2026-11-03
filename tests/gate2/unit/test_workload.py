import hashlib
import json
import builtins
import socket
import time

import pytest

from gate2.workload import WorkloadError, WorkloadSpec, generate


IDENTITY = {
    "f01_sha": "345f9526d54f4fbd582c15f4f0b613bc8ab3996e",
    "c04_sha": "5d482a1016b97d663c57ad31d8bac21c19c8c799",
    "e05_sha": "e52b91d38a9f9c6651a4203eccbe59b03d908905",
    "config_digest": "a" * 64,
}


def test_fixture_preserves_accepted_f01_sha():
    fixture = generate(spec())
    assert fixture.spec.f01_sha == IDENTITY["f01_sha"]
    assert fixture.spec.c04_sha == IDENTITY["c04_sha"]
    assert fixture.spec.e05_sha == IDENTITY["e05_sha"]


def spec(**changes):
    values = dict(jobs=2, stages=3, artifact_bytes=16, cost_units=4,
                  fault_position=1, seed=73, concurrency=1, repetitions=2,
                  **IDENTITY)
    values.update(changes)
    return WorkloadSpec(**values)


def test_same_complete_identity_has_identical_bytes_digest_and_fault_schedule():
    left, right = generate(spec()), generate(spec())
    assert left.to_bytes() == right.to_bytes()
    assert left.fixture_digest == right.fixture_digest
    assert left.fault_schedule == right.fault_schedule
    assert hashlib.sha256(left.to_bytes()).hexdigest() == left.fixture_digest


@pytest.mark.parametrize("change", [
    {"f01_sha": "1" * 40}, {"c04_sha": "2" * 40},
    {"e05_sha": "3" * 40}, {"config_digest": "b" * 64},
    {"seed": 74}, {"jobs": 3}, {"stages": 4},
    {"artifact_bytes": 17}, {"cost_units": 5},
    {"fault_position": 2}, {"repetitions": 3},
])
def test_any_identity_or_dimension_change_changes_generation(change):
    baseline = generate(spec())
    changed = generate(spec(**change))
    assert changed.to_bytes() != baseline.to_bytes()
    assert changed.fixture_digest != baseline.fixture_digest


@pytest.mark.parametrize("change", [
    {"jobs": 0}, {"jobs": 101}, {"stages": 0}, {"stages": 21},
    {"artifact_bytes": 0}, {"artifact_bytes": 1_000_001},
    {"cost_units": 0}, {"cost_units": 1_000_001},
    {"fault_position": 3}, {"concurrency": 0}, {"concurrency": 2},
    {"repetitions": 0}, {"repetitions": 101},
])
def test_dimensions_are_explicitly_bounded(change):
    with pytest.raises(WorkloadError):
        spec(**change)


def test_fixture_is_generated_data_and_does_not_encode_runtime_provenance():
    fixture = generate(spec())
    payload = json.loads(fixture.to_bytes())
    assert fixture.uses_wall_clock is False
    assert all(stage.artifact for job in fixture.jobs for stage in job.stages)
    assert "source_system" not in payload
    assert "created_at" not in payload
    assert payload["identity"] == IDENTITY


def test_generation_does_not_open_files_use_network_or_read_clock(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("generation attempted external/runtime I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(time, "time", forbidden)
    assert generate(spec()).fixture_digest
