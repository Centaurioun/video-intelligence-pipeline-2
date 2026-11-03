import math

import pytest

from gate0.arms.semantic import RepresentationRecord
from gate0.ranking import RankingError, rank_candidates
from gate0.temporal import Rational


def rep(rid, revision, window, vector, *, start=Rational(0, 1), status="SUCCEEDED"):
    return RepresentationRecord(
        space_id="semantic_visual", representation_id=rid, revision_id=revision,
        window_id=window, sampling_manifest_digest="a" * 64,
        model_identity="local", processor_digest="b" * 64,
        preprocessing_digest="c" * 64, pooling="MEAN_TARGET_SLOTS",
        dimension=len(vector) if vector is not None else 0, dtype="float64",
        normalization="L2", metric="COSINE", generation_attempt_id="attempt",
        representation_status=status, failure_reason=None if status == "SUCCEEDED" else "SAMPLE_FAILED",
        vector_digest="d" * 64 if status == "SUCCEEDED" else None,
        vector_digest_algorithm="SHA-256" if status == "SUCCEEDED" else None,
        vector_encoding="float64_le_row_major" if status == "SUCCEEDED" else None,
        vector_length=len(vector) if status == "SUCCEEDED" else None,
        accumulation_order="target_tick_ascending_serial" if status == "SUCCEEDED" else None,
    )


def test_rank_candidates_uses_exact_cosine_and_frozen_total_tie_order():
    rows = [
        rep("c2", "rev-b", "w2", (0.0, 1.0), start=Rational(1, 2)),
        rep("c1", "rev-a", "w9", (1.0, 0.0), start=Rational(2, 4)),
        rep("c3", "rev-a", "w1", (1.0, 0.0), start=Rational(1, 2)),
    ]
    result = rank_candidates((1.0, 0.0), rows, query_id="q1", vectors={"c2": (0.0, 1.0), "c1": (1.0, 0.0), "c3": (1.0, 0.0)})
    assert [item.candidate_id for item in result] == ["c3", "c1", "c2"]
    assert result[0].score == 1.0
    assert result[0].gold_accessed is False
    assert result[0].representation_id == "c3"


def test_failed_vectors_are_retained_as_status_rows_but_not_primary_rank():
    rows = [rep("ok", "r", "w", (1.0, 0.0)), rep("bad", "r", "w2", None, status="FAILED")]
    result = rank_candidates((1.0, 0.0), rows, query_id="q", vectors={"ok": (1.0, 0.0)})
    assert [item.candidate_id for item in result] == ["ok", "bad"]
    assert result[0].rank == 1 and result[0].score == 1.0
    assert result[1].rank is None and result[1].score is None
    assert result[1].score_status == "FAILED"


def test_failed_vector_status_row_keeps_null_score_rank_and_failed_coverage():
    result = rank_candidates((1.0, 0.0), [rep("bad", "r", "w", None, status="FAILED")],
                             query_id="q")
    assert len(result) == 1
    row = result[0]
    assert row.score is None
    assert row.rank is None
    assert row.score_status == "FAILED"
    assert row.coverage_status == "FAILED"


@pytest.mark.parametrize("vector", [(math.nan, 0.0), (math.inf, 0.0), (0.0, 0.0)])
def test_nonfinite_or_zero_vectors_remain_failed_status_rows(vector):
    row = rep("bad", "r", "w", vector)
    with pytest.raises(RankingError, match="rank-eligible representation"):
        rank_candidates((1.0, 0.0), [row], query_id="q", vectors={"bad": vector})


def test_non_normalized_vectors_are_rejected():
    with pytest.raises(RankingError, match="normalized"):
        rank_candidates((1.0, 0.0), [rep("bad", "r", "w", (2.0, 0.0))], query_id="q", vectors={"bad": (2.0, 0.0)})


def test_colliding_total_order_key_is_an_error():
    rows = [rep("same", "r", "w", (1.0, 0.0)), rep("same", "r", "w", (1.0, 0.0))]
    with pytest.raises(RankingError, match="collision"):
        rank_candidates((1.0, 0.0), rows, query_id="q", vectors={"same": (1.0, 0.0)})


def test_rational_window_start_is_reduced_for_ties():
    rows = [rep("later", "r", "w2", (1.0, 0.0), start=Rational(1, 2)), rep("earlier", "r", "w1", (1.0, 0.0), start=Rational(2, 4))]
    result = rank_candidates((1.0, 0.0), rows, query_id="q", vectors={"later": (1.0, 0.0), "earlier": (1.0, 0.0)}, window_starts={"later": (1, 2), "earlier": (2, 4)})
    assert [item.candidate_id for item in result] == ["earlier", "later"]
    assert result[0].tie_key[2] == (1, 2)


def test_ranker_does_not_accept_gold_or_judgment_inputs():
    with pytest.raises(TypeError):
        rank_candidates((1.0, 0.0), [], query_id="q", gold_events=())


# ---------------------------------------------------------------------------
# D8 semantic-identity closure at the producer boundary
# ---------------------------------------------------------------------------
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

from gate0.execution import execute_stage  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
PRODUCER_FIXTURE_ROOT = REPO_ROOT / "tests/gate0/fixtures/synthetic-input"
if str(PRODUCER_FIXTURE_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCER_FIXTURE_ROOT))
import generate  # noqa: E402

METADATA_PAYLOAD_KEYS = {
    "candidate_id", "query_id", "arm_id", "window_id", "score", "score_status",
    "rank", "coverage_status", "gold_accessed",
}
SEMANTIC_PAYLOAD_KEYS = METADATA_PAYLOAD_KEYS | {"representation_id"}
TWO_ARM_REGISTRY = [
    {"arm_id": "metadata-floor", "representation_kind": "metadata_floor"},
    {"arm_id": "offline-development-arm", "representation_kind": "embedding"},
]


def _produced_rank_run(tmp_path):
    input_root = tmp_path / "inputs"
    output_root = tmp_path / "outputs"
    output_root.mkdir()
    generate.write_fixtures(input_root)
    run_id = "run_producer_rank"
    run = output_root / run_id
    config_path = REPO_ROOT / "config/gate0/default.json"
    for stage in ("prepare", "inventory", "split", "label", "preflight", "extract", "embed", "rank"):
        code, _projection = execute_stage(
            stage, run=run, config_path=config_path, input_root=input_root,
            output_root=output_root, run_id=run_id,
        )
        assert code == 0, stage
    manifest = json.loads((run / "run_manifest.json").read_text(encoding="utf-8"))
    rows = [json.loads(line)["payload"]
            for line in (run / "ranked_candidates.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()]
    return manifest, rows


def test_produced_run_declares_the_closed_two_arm_registry(tmp_path):
    manifest, _rows = _produced_rank_run(tmp_path)
    assert manifest["arms"] == TWO_ARM_REGISTRY
    assert "arms" not in json.loads(
        (REPO_ROOT / "schemas/gate0/run_manifest.json").read_text(encoding="utf-8"))["required"]


def test_metadata_floor_payload_has_no_representation_or_duplicate_coordinates(tmp_path):
    _manifest, rows = _produced_rank_run(tmp_path)
    metadata = [row for row in rows if row["arm_id"] == "metadata-floor"]
    assert metadata, "the metadata floor must be scored"
    for row in metadata:
        assert set(row) == METADATA_PAYLOAD_KEYS, row
        assert "representation_id" not in row
        for removed in ("revision_id", "start", "end", "mapping_ref", "origin", "time_base",
                        "input_artifact_refs"):
            assert removed not in row


def test_semantic_payload_carries_a_resolvable_representation_identity(tmp_path):
    manifest, rows = _produced_rank_run(tmp_path)
    representations = {rep["representation_id"]: rep for rep in manifest["representations"]}
    semantic = [row for row in rows if row["arm_id"] == "offline-development-arm"]
    assert semantic, "the semantic arm must be scored"
    for row in semantic:
        assert set(row) == SEMANTIC_PAYLOAD_KEYS, row
        rep = representations[row["representation_id"]]
        assert rep["representation_status"] == "SUCCEEDED"
        assert rep["window_id"] == row["window_id"]


def test_produced_candidate_ids_are_one_to_one_identities(tmp_path):
    manifest, rows = _produced_rank_run(tmp_path)
    candidate_ids = [row["candidate_id"] for row in rows]
    assert len(candidate_ids) == len(set(candidate_ids))
    # candidate identity is not the representation identity
    assert not (set(candidate_ids) & {rep["representation_id"] for rep in manifest["representations"]})


def test_semantic_arm_id_mismatch_is_refused():
    """A diverging configured semantic arm id surfaces instead of diverging."""
    from gate0.execution import _arm_registry

    with pytest.raises(ValueError, match="^SEMANTIC_ARM_ID_MISMATCH:"):
        _arm_registry({"model": {"semantic_arm_id": "diverging-arm"}})
