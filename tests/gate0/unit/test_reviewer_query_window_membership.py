"""Synthetic run membership checks for reviewer query/window references."""
from __future__ import annotations

import json
from pathlib import Path

from gate0.config_freeze import canonical_config_digest
from gate0.contracts.types import payload_digest
from gate0.evaluation import _input_digest_for, _mapping_digest_for
from gate0.execution import _stage_evaluate
from gate0.labels import label_version_digest


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = REPO_ROOT / "config/gate0/default.json"
REVIEWERS = ("reviewer-1", "reviewer-2")
TOKENS = ("arm-a", "arm-b")
FAMILIES = ("APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT")


def _fixture(tmp_path: Path, *, unknown: str | None, reviewed_count: int = 24,
             sample_window_count: int = 24) -> tuple[Path, dict, dict]:
    config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    config["policy"]["review_input"]["authorized_root"] = str(authorized)
    config_digest = canonical_config_digest(config)
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    queries = [
        {"query_id": f"q{i}", "text": f"query {i}", "family": FAMILIES[i // 6],
         "presence": "POSITIVE", "split": "EVALUATION"}
        for i in range(24)
    ]
    windows = [
        {"window_id": f"w{i}", "revision_id": f"rev{i}", "start": i, "end": i + 1,
         "origin": {"numerator": 0, "denominator": 1},
         "time_base": {"numerator": 1, "denominator": 1}, "mapping_ref": "mapping-synthetic"}
        for i in range(24)
    ]
    (run_dir / "queries.jsonl").write_text("".join(json.dumps({"payload": q}) + "\n" for q in queries), encoding="utf-8")
    (run_dir / "gold_events.jsonl").write_text("", encoding="utf-8")
    (run_dir / "ranked_candidates.jsonl").write_text("", encoding="utf-8")
    sample_records = sorted([
        {"record_id": f"sample-{i}", "record_type": "sample_target", "record_schema_version": "gate0.v1",
         "record_digest": "a" * 64, "payload": {"window_id": f"w{i}"}}
        for i in range(sample_window_count)
    ], key=lambda record: record["record_id"])
    (run_dir / "window_sample_manifest.jsonl").write_text(
        "".join(json.dumps(record) + "\n" for record in sample_records), encoding="utf-8")

    token_map = [dict(row) for row in config["blinding"]["token_map"]]
    rows = []
    for i in range(reviewed_count):
        query_id = "q_unknown" if unknown == "query_id" and i == 0 else f"q{i}"
        window_id = "w_unknown" if unknown == "window_id" and i == 0 else f"w{i}"
        for token in TOKENS:
            for reviewer_id in REVIEWERS:
                rows.append({
                    "assertion_id": f"assertion-{i}-{token}", "query_id": query_id, "window_id": window_id,
                    "blind_arm_token": token, "reviewer_id": reviewer_id, "grade": 2,
                    "ambiguity": "NONE", "review_status": "ACCEPTED",
                    "assertion": {"version": "v1", "text": f"synthetic query {i}", "digest": "d" * 64},
                })
    mapping_digest = _mapping_digest_for(token_map,
        mapping_version=str(config["blinding"]["mapping_version"]), config_digest=config_digest)
    envelope = {
        "schema_version": "gate0.reviewer-input.v1",
        "input_digest": _input_digest_for("gate0.reviewer-input.v1", rows),
        "blind_mapping_digest": mapping_digest,
        "rows": rows,
    }
    review_path = authorized / "review.json"
    review_path.write_text(json.dumps(envelope), encoding="utf-8")
    manifest = {
        "run_id": "run_synthetic_membership", "config_digest": config_digest,
        "ranking_digest": "1" * 64, "baseline_digest": "2" * 64,
        "gold_version_digest": "3" * 64, "query_version_digest": label_version_digest(queries),
        "windows": windows, "policy_decision_ids": ["policy-a", "policy-b"],
        "runtime": {"tool_environment_digest": "5" * 64},
        "sample_manifest_digest": payload_digest(sample_records, "window_sample_manifest.jsonl"),
    }
    return run_dir, config, {"review_path": review_path, "manifest": manifest, "config_path": tmp_path / "config.json"}


def _evaluate(tmp_path: Path, *, unknown: str | None, reviewed_count: int = 24,
              sample_window_count: int = 24, tamper_queries: bool = False):
    run_dir, config, context = _fixture(tmp_path, unknown=unknown, reviewed_count=reviewed_count,
                                       sample_window_count=sample_window_count)
    if tamper_queries:
        lines = (run_dir / "queries.jsonl").read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["payload"]["query_id"] = "q_substituted"
        lines[0] = json.dumps(first)
        (run_dir / "queries.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return _stage_evaluate(run_dir, context["manifest"], config, context["config_path"], context["review_path"])


def test_evaluation_refuses_reviewer_query_outside_prepared_query_set(tmp_path: Path) -> None:
    code, projection = _evaluate(tmp_path, unknown="query_id")
    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "REVIEW_INPUT:unknown reviewer query_id"


def test_evaluation_refuses_reviewer_window_outside_measured_window_set(tmp_path: Path) -> None:
    code, projection = _evaluate(tmp_path, unknown="window_id")
    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "REVIEW_INPUT:unknown reviewer window_id"


def test_evaluation_does_not_require_every_measured_window_to_be_judged(tmp_path: Path) -> None:
    # Membership is a foreign-key check. This does not make window-catalog
    # coverage a prerequisite for a synthetic evaluation envelope.
    code, projection = _evaluate(tmp_path, unknown=None, reviewed_count=1)
    assert code == 0
    assert projection["status"] == "SUCCEEDED"


def test_evaluation_refuses_window_when_canonical_sample_manifest_is_empty(tmp_path: Path) -> None:
    code, projection = _evaluate(tmp_path, unknown=None, sample_window_count=0)
    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "REVIEW_INPUT:unknown reviewer window_id"


def test_evaluation_refuses_queries_that_do_not_match_frozen_digest(tmp_path: Path) -> None:
    code, projection = _evaluate(tmp_path, unknown=None, tamper_queries=True)
    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "QUERY_VERSION_DIGEST_MISMATCH"
