"""D8 F2/F3 closure: window referential integrity and per-kind arm presence.

F2: every ``window_id`` referenced by ``ranked_candidates.jsonl`` and
``window_judgments.jsonl`` must resolve to at least one ``sample_target`` record
in ``window_sample_manifest.jsonl`` (the canonical technical-window owner).
A window is valid for any coverage_status, including FAILED/OMITTED; it does
not have to contain a successfully decoded sample.

F3: when ``ranked_candidates.jsonl`` has rows, every arm declared in the closed
``run_manifest.json`` ``arms`` registry must contribute at least one ranked row
of its resolved representation kind.  Status/failed/zero-vector rows count as
representation of their kind.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from gate0.contracts.validator import ARTIFACT_FILENAMES, ContractError, validate_artifact_set

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/gate0/fixtures/semantic-closure"


# ---------------------------------------------------------------------------
# Local fixture builder (kept local so shared unit tests stay untouched).
# ---------------------------------------------------------------------------

def _candidate() -> dict:
    candidate: dict = {}
    for name in ARTIFACT_FILENAMES:
        path = FIXTURE / name
        if name.endswith(".jsonl"):
            candidate[name] = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        elif name.endswith(".md"):
            candidate[name] = path.read_text()
        else:
            candidate[name] = json.loads(path.read_text())
    return candidate


def _run(candidate: dict) -> dict:
    return candidate["run_manifest.json"]


def _ranked_records(candidate: dict) -> list[dict]:
    return candidate["ranked_candidates.jsonl"]


def _ranked(candidate: dict) -> list[dict]:
    return [record["payload"] for record in _ranked_records(candidate)]


def _ranked_by_arm(candidate: dict, arm_id: str) -> dict:
    return next(payload for payload in _ranked(candidate) if payload["arm_id"] == arm_id)


def _status_candidate() -> dict:
    """Candidate whose embedding arm has only FAILED sampling evidence."""
    candidate = _candidate()
    sampling = candidate["window_sample_manifest.jsonl"]
    sampling.append({"target_id": "target_window_2_t0", "window_id": "window_2", "interval_id": "interval_0",
                     "tick": 0, "coverage_status": "FAILED", "pts_status": "NO_COVERAGE"})
    sampling.append({"target_id": "target_window_2_t1", "window_id": "window_2", "interval_id": "interval_0",
                     "tick": 1, "coverage_status": "OMITTED", "pts_status": "NO_COVERAGE"})
    representations = _run(candidate)["representations"]
    failed = json.loads(json.dumps(representations[0]))
    failed.update({"representation_id": "representation_2", "window_id": "window_2",
                   "representation_status": "FAILED"})
    representations.append(failed)
    row = _ranked_by_arm(candidate, "offline-development-arm")
    row.update({"window_id": "window_2", "representation_id": "representation_2",
                "score": None, "rank": None, "score_status": "FAILED",
                "coverage_status": "FAILED"})
    return candidate


# ---------------------------------------------------------------------------
# F2 — window referential integrity (canonical owner: window_sample_manifest).
# ---------------------------------------------------------------------------

def test_metadata_ranked_row_with_unknown_window_id_fails():
    candidate = _candidate()
    _ranked_by_arm(candidate, "metadata-floor")["window_id"] = "window_nonexistent"
    with pytest.raises(ContractError, match="window_sample_manifest"):
        validate_artifact_set(candidate)


def test_window_judgment_with_unknown_window_id_fails():
    candidate = _candidate()
    candidate["window_judgments.jsonl"][0]["window_id"] = "window_nonexistent"
    with pytest.raises(ContractError, match="window_sample_manifest"):
        validate_artifact_set(candidate)


def test_representation_revision_must_resolve_to_source_manifest():
    candidate = _candidate()
    _run(candidate)["representations"][0]["revision_id"] = "rev_unknown"
    with pytest.raises(ContractError, match="source_manifest"):
        validate_artifact_set(candidate)


def test_status_row_may_reference_a_window_with_only_failed_sampling():
    """A window is valid for any coverage_status; non-FINITE status rows pass."""
    validate_artifact_set(_status_candidate())


def test_complete_two_arm_candidate_passes_window_and_arm_validation():
    assert validate_artifact_set(_candidate()) is True


def test_cli_foreign_keys_rejects_unresolved_window_id(tmp_path):
    root = tmp_path / "candidate"
    shutil.copytree(FIXTURE, root)
    path = root / "ranked_candidates.jsonl"
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for record in records:
        if record["payload"]["arm_id"] == "metadata-floor":
            record["payload"]["window_id"] = "window_nonexistent"
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")
    result = subprocess.run([sys.executable, "scripts/verify-gate0.py", "--foreign-keys",
                             "--candidate-root", str(root)], cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 30
    assert "window_sample_manifest" in result.stderr


# ---------------------------------------------------------------------------
# F3 — per-kind arm presence for ranked candidates (D8-1 / ADR D03).
# ---------------------------------------------------------------------------

def test_both_arms_declared_metadata_only_ranked_rows_fail():
    candidate = _candidate()
    candidate["ranked_candidates.jsonl"] = [record for record in _ranked_records(candidate)
                                            if record["payload"]["arm_id"] == "metadata-floor"]
    with pytest.raises(ContractError, match="declared arm"):
        validate_artifact_set(candidate)


def test_both_arms_declared_embedding_only_ranked_rows_fail():
    candidate = _candidate()
    candidate["ranked_candidates.jsonl"] = [record for record in _ranked_records(candidate)
                                            if record["payload"]["arm_id"] == "offline-development-arm"]
    with pytest.raises(ContractError, match="declared arm"):
        validate_artifact_set(candidate)


def test_duplicate_and_undeclared_arms_still_fail():
    candidate = _candidate()
    _run(candidate)["arms"].append({"arm_id": "metadata-floor", "representation_kind": "embedding"})
    with pytest.raises(ContractError, match="duplicate arm"):
        validate_artifact_set(candidate)

    candidate = _candidate()
    _ranked(candidate)[0]["arm_id"] = "undeclared-arm"
    with pytest.raises(ContractError, match="arm"):
        validate_artifact_set(candidate)


def test_empty_ranked_and_judgment_artifacts_before_ranking_pass():
    candidate = _candidate()
    candidate["ranked_candidates.jsonl"] = []
    candidate["window_judgments.jsonl"] = []
    assert validate_artifact_set(candidate) is True


def test_non_finite_status_rows_satisfy_presence_for_their_kind():
    assert validate_artifact_set(_status_candidate()) is True
