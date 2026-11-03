"""PKT-D2-3 characterization: editor-query / human-gold loader conformance.

This module is characterization-first: it proves what the *existing unwired*
label-input seams already enforce (``gate0.execution.load_editor_queries``,
``load_human_gold``, ``_authorized_query_cardinality``,
``prepare_authorized_label_inputs``) and separately pins the frozen builders in
``gate0.labels`` (``build_queries``, ``build_gold_events``).  Nothing here is
production code; every fixture is synthetic metadata in ``tmp_path``.

Gap verdicts used in comments:

  ENFORCED              rejected today with a typed reason / ValueError.
  NOT_ENFORCED          accepted (or wrongly rejected) today -- a real gap.
  NOT_OBSERVED          structurally unobservable from the declared metadata.
                        No authenticity/provenance check is invented here.

Tests are deterministic: no wall clock, randomness, network, real media or model.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gate0 import execution
from gate0 import labels
from gate0 import media_experiment
from gate0.media_experiment import AuthorizedLocalError, load_authorized_local_declaration

FAMILIES = (
    "APPEARANCE",
    "VISIBLE_ACTION",
    "INTERACTION",
    "SCENE_COMPOSITION_CAMERA_MOVEMENT",
)
EDITOR_QUERIES_SCHEMA = "gate0.editor-queries.v1"
HUMAN_GOLD_SCHEMA = "gate0.human-gold.v1"
CARDINALITY_REASON = "AUTHORIZED_QUERY_CARDINALITY_INVALID"


# ---------------------------------------------------------------------------
# synthetic builders (copied in-lane from the D-1 fixture style; no test import)
# ---------------------------------------------------------------------------

def _queries_document(*, dev_presence: str = "POSITIVE",
                      positive_counts: dict[str, int] | None = None,
                      absent_count: int = 8,
                      query_version: str = "editor-v1") -> dict:
    counts = positive_counts or {family: 6 for family in FAMILIES}
    queries: list[dict] = []
    for family in FAMILIES:
        for index in range(counts[family]):
            queries.append({
                "query_id": f"q_eval_{family.lower()}_{index}",
                "text": f"editor query {family} {index}",
                "family": family,
                "presence": "POSITIVE",
                "split": "EVALUATION",
            })
    for index in range(absent_count):
        queries.append({
            "query_id": f"q_eval_absent_{index}",
            "text": f"editor absent query {index}",
            "family": FAMILIES[index % 4],
            "presence": "ABSENT",
            "split": "EVALUATION",
        })
    for index in range(8):
        queries.append({
            "query_id": f"q_dev_{index}",
            "text": f"editor development query {index}",
            "family": FAMILIES[index % 4],
            "presence": dev_presence,
            "split": "DEVELOPMENT",
        })
    return {"schema_version": EDITOR_QUERIES_SCHEMA, "query_version": query_version,
            "queries": queries}


def _gold_event(query_id: str, reviewer_id: str, *, grade: int = 2,
                revision_id: str = "rev_eval_alpha", start=(0, 1), end=(2, 1),
                **optional) -> dict:
    event = {
        "query_id": query_id,
        "revision_id": revision_id,
        "reviewer_id": reviewer_id,
        "grade": grade,
        "rationale": f"human rationale from {reviewer_id}",
        "stream_index": 0,
        "start": start,
        "end": end,
        "uncertainty": {
            "start": {"numerator": 0, "denominator": 1},
            "end": {"numerator": 2, "denominator": 1},
        },
    }
    event.update(optional)
    return event


def _gold_document(events: list[dict] | None = None) -> dict:
    if events is None:
        events = []
        for query_id in ("q_eval_appearance_0", "q_eval_visible_action_0"):
            for reviewer_id in ("reviewer_a", "reviewer_b"):
                events.append(_gold_event(query_id, reviewer_id))
    return {"schema_version": HUMAN_GOLD_SCHEMA, "label_version": "human-gold-v1",
            "events": events}


def _declaration(tmp_path: Path):
    document = {
        "schema_version": media_experiment.AUTHORIZED_CORPUS_SCHEMA_VERSION,
        "corpus_kind": media_experiment.AUTHORIZED_CORPUS_KIND,
        "revisions": [
            {"revision_id": "rev_eval_alpha", "occurrence_id": "occ_eval_alpha",
             "content_id": "content_eval_alpha", "locator": "media/alpha.mp4",
             "relation_ids": [], "split": "EVALUATION", "window_count": 2,
             "selected_stream_index": 0, "declared_byte_count": None,
             "declared_content_sha256": None},
            {"revision_id": "rev_dev_probe", "occurrence_id": "occ_dev_probe",
             "content_id": "content_dev_probe", "locator": "media/probe.mp4",
             "relation_ids": [], "split": "DEVELOPMENT", "window_count": 1,
             "selected_stream_index": 0, "declared_byte_count": None,
             "declared_content_sha256": None},
        ],
        "relations": [],
        "evaluation_revision_ids": ["rev_eval_alpha"],
        "development_revision_id": "rev_dev_probe",
        "provenance": {"declaration_authority": "gate0-owner"},
        "policy": {"local_only": True},
    }
    root = tmp_path / "inputs"
    root.mkdir(exist_ok=True)
    path = root / media_experiment.AUTHORIZED_CORPUS_FILE
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _write(tmp_path: Path, name: str, document: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def _prepare(tmp_path: Path, *, queries: dict | None = None, gold: dict | None = None):
    queries_path = _write(tmp_path, "editor-queries.json", queries or _queries_document())
    gold_path = _write(tmp_path, "human-gold.json", gold or _gold_document())
    declaration = load_authorized_local_declaration(_declaration(tmp_path))
    return execution.prepare_authorized_label_inputs(
        declaration=declaration,
        editor_queries_path=queries_path,
        human_gold_path=gold_path,
    )


def _built_queries() -> tuple[dict, ...]:
    document = _queries_document()
    specs = [(row["query_id"], row["text"], (row["family"], row["presence"]))
             for row in document["queries"]]
    split_by_id = {row["query_id"]: row["split"] for row in document["queries"]}
    return labels.build_queries(specs, split_by_id, "editor-v1")


def _cardinality_rows(*, positive_counts: dict[str, int] | None = None,
                      absent: int = 8, development: int = 8,
                      families: tuple[str, ...] = FAMILIES) -> list[dict]:
    """Payload-shaped rows for the prep-time cardinality guard."""
    counts = positive_counts or {family: 6 for family in families}
    rows = []
    for family in families:
        for _ in range(counts[family]):
            rows.append({"family": family, "presence": "POSITIVE", "split": "EVALUATION"})
    for _ in range(absent):
        rows.append({"family": families[0], "presence": "ABSENT", "split": "EVALUATION"})
    for _ in range(development):
        rows.append({"family": families[0], "presence": "POSITIVE", "split": "DEVELOPMENT"})
    return rows


# ---------------------------------------------------------------------------
# 1. positive-count / family-distribution cardinality
# ---------------------------------------------------------------------------

def test_build_queries_rejects_23_and_25_evaluation_positives():
    """ENFORCED (frozen builder): the 24-positive total is pinned.

    23 positives forces 9 absent and 25 forces 7 absent to stay at 40 queries;
    both shapes reach ``build_queries`` and are rejected there.
    """
    for document in (
        _queries_document(positive_counts={"APPEARANCE": 6, "VISIBLE_ACTION": 6,
                                           "INTERACTION": 6,
                                           "SCENE_COMPOSITION_CAMERA_MOVEMENT": 5},
                          absent_count=9),
        _queries_document(positive_counts={"APPEARANCE": 6, "VISIBLE_ACTION": 6,
                                           "INTERACTION": 6,
                                           "SCENE_COMPOSITION_CAMERA_MOVEMENT": 7},
                          absent_count=7),
    ):
        assert len(document["queries"]) == 40
        specs = [(row["query_id"], row["text"], (row["family"], row["presence"]))
                 for row in document["queries"]]
        split_by_id = {row["query_id"]: row["split"] for row in document["queries"]}
        with pytest.raises(ValueError, match="invalid query cardinality"):
            labels.build_queries(specs, split_by_id, "editor-v1")


@pytest.mark.parametrize("positive_counts, expected_detail", [
    ({"APPEARANCE": 6, "VISIBLE_ACTION": 6, "INTERACTION": 6,
      "SCENE_COMPOSITION_CAMERA_MOVEMENT": 5}, "POSITIVE 5 != 6"),
    ({"APPEARANCE": 6, "VISIBLE_ACTION": 6, "INTERACTION": 6,
      "SCENE_COMPOSITION_CAMERA_MOVEMENT": 7}, "POSITIVE 7 != 6"),
])
def test_cardinality_guard_rejects_23_and_25_positives(positive_counts, expected_detail):
    """ENFORCED: 23/25 positives are rejected by the per-family guard.

    A valid 40-query shape can never carry 23 or 25 positives without breaking
    the six-per-family distribution, so this is the guard that fires.
    """
    rows = _cardinality_rows(positive_counts=positive_counts,
                             absent=32 - sum(positive_counts.values()))
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(rows)
    assert excinfo.value.reason == CARDINALITY_REASON
    assert expected_detail in excinfo.value.detail


def test_cardinality_guard_accepts_24_positives_six_per_family():
    """ENFORCED: the contract set (24 positives, 6 per family) is accepted."""
    assert execution._authorized_query_cardinality(_cardinality_rows()) is None


def test_cardinality_guard_rejects_five_per_family_and_accepts_six():
    """ENFORCED: per-family skew (5 and, balancing it, 7) is rejected; 6 accepted.

    ``build_queries`` only sees totals, so the per-family rule lives in the
    prep-time guard.  A 5/7 split keeps the 24 total but is still rejected.
    """
    skewed = _cardinality_rows(positive_counts={
        "APPEARANCE": 5, "VISIBLE_ACTION": 7, "INTERACTION": 6,
        "SCENE_COMPOSITION_CAMERA_MOVEMENT": 6})
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(skewed)
    assert excinfo.value.reason == CARDINALITY_REASON
    assert "POSITIVE 5 != 6" in excinfo.value.detail


def test_prepare_rejects_five_per_family_skew(tmp_path):
    """ENFORCED via prepare: 5/7 family split reaches the guard and is refused."""
    document = _queries_document(positive_counts={
        "APPEARANCE": 5, "VISIBLE_ACTION": 7, "INTERACTION": 6,
        "SCENE_COMPOSITION_CAMERA_MOVEMENT": 6})
    with pytest.raises(AuthorizedLocalError) as excinfo:
        _prepare(tmp_path, queries=document)
    assert excinfo.value.reason == CARDINALITY_REASON
    assert "POSITIVE 5 != 6" in excinfo.value.detail


def test_guard_reports_evaluation_positive_total():
    """ENFORCED: a 3-family (18-positive) set trips the total-positive check."""
    rows = _cardinality_rows(
        positive_counts={"APPEARANCE": 6, "VISIBLE_ACTION": 6, "INTERACTION": 6},
        families=("APPEARANCE", "VISIBLE_ACTION", "INTERACTION"))
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(rows)
    assert excinfo.value.reason == CARDINALITY_REASON
    assert "EVALUATION POSITIVE 18 != 24" in excinfo.value.detail


# ---------------------------------------------------------------------------
# 2. absent split (must be EVALUATION, exactly 8)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("absent, expected_detail", [
    (7, "EVALUATION ABSENT 7 != 8"),
    (9, "EVALUATION ABSENT 9 != 8"),
])
def test_cardinality_guard_rejects_7_and_9_absent(absent, expected_detail):
    """ENFORCED: exactly 8 EVALUATION absent queries."""
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(_cardinality_rows(absent=absent))
    assert excinfo.value.reason == CARDINALITY_REASON
    assert expected_detail in excinfo.value.detail


def test_absent_count_eight_is_accepted():
    """ENFORCED: the contract absent count is accepted."""
    assert execution._authorized_query_cardinality(_cardinality_rows(absent=8)) is None


def test_build_queries_rejects_absent_skew():
    """ENFORCED (frozen builder): 7/9 absent cannot form the 40-query set."""
    for absent_count in (7, 9):
        document = _queries_document(absent_count=absent_count)
        assert len(document["queries"]) != 40
        specs = [(row["query_id"], row["text"], (row["family"], row["presence"]))
                 for row in document["queries"]]
        split_by_id = {row["query_id"]: row["split"] for row in document["queries"]}
        with pytest.raises(ValueError, match="expected exactly 40 queries"):
            labels.build_queries(specs, split_by_id, "editor-v1")


def test_absent_development_rows_are_accepted_gap(tmp_path):
    """GAP (NOT_ENFORCED): ABSENT queries on the DEVELOPMENT split are accepted.

    The frozen builder only constrains the EVALUATION positive total, and the
    prep-time guard counts absent rows only inside the EVALUATION split, so a
    package with eight ABSENT *development* queries plus the contract EVALUATION
    set passes end to end.  The A3 contract treats absent queries as an
    EVALUATION-only presence class; nothing enforces it.
    """
    document = _queries_document(dev_presence="ABSENT")
    projection = _prepare(tmp_path, queries=document)
    development = [record["payload"] for record in projection["queries"]
                   if record["payload"]["split"] == "DEVELOPMENT"]
    assert len(development) == 8
    assert {row["presence"] for row in development} == {"ABSENT"}
    # The loader also accepts these rows verbatim (no split/presence rule).
    rows = execution.load_editor_queries(
        _write(tmp_path, "editor-queries.json", document))
    assert {row["presence"] for row in rows if row["split"] == "DEVELOPMENT"} == {
        "ABSENT"}
    # And the guard the prepare seam calls accepts the ABSENT dev rows too.
    assert execution._authorized_query_cardinality(
        [{"family": row["family"], "presence": row["presence"], "split": row["split"]}
         for row in document["queries"]]) is None


# ---------------------------------------------------------------------------
# 3. development split (exactly 8)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("development, expected_detail", [
    (7, "DEVELOPMENT 7 != 8"),
    (9, "DEVELOPMENT 9 != 8"),
])
def test_cardinality_guard_rejects_7_and_9_development(development, expected_detail):
    """ENFORCED: exactly 8 DEVELOPMENT queries."""
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(_cardinality_rows(development=development))
    assert excinfo.value.reason == CARDINALITY_REASON
    assert expected_detail in excinfo.value.detail


def test_development_count_eight_is_accepted():
    """ENFORCED: the contract development count is accepted."""
    assert execution._authorized_query_cardinality(_cardinality_rows(development=8)) is None


def test_build_queries_rejects_development_skew():
    """ENFORCED (frozen builder): 7/9 development queries break the 40 total."""
    for development in (7, 9):
        document = _queries_document()
        if development == 7:
            document["queries"] = [row for row in document["queries"]
                                   if row["split"] != "DEVELOPMENT" or row["query_id"] != "q_dev_7"]
        else:
            document["queries"].append({"query_id": "q_dev_extra",
                                        "text": "extra development query",
                                        "family": FAMILIES[0], "presence": "POSITIVE",
                                        "split": "DEVELOPMENT"})
        specs = [(row["query_id"], row["text"], (row["family"], row["presence"]))
                 for row in document["queries"]]
        split_by_id = {row["query_id"]: row["split"] for row in document["queries"]}
        with pytest.raises(ValueError, match="expected exactly 40 queries"):
            labels.build_queries(specs, split_by_id, "editor-v1")


# ---------------------------------------------------------------------------
# 4. duplicate identities
# ---------------------------------------------------------------------------

def test_duplicate_query_id_rejected_by_loader(tmp_path):
    """ENFORCED: the editor-query loader pins query_id uniqueness."""
    document = _queries_document()
    document["queries"].append(dict(document["queries"][0], text="an extra text"))
    path = _write(tmp_path, "editor-queries.json", document)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_editor_queries(path)
    assert excinfo.value.reason == "AUTHORIZED_EDITOR_QUERIES_INVALID"
    assert "duplicate query_id" in excinfo.value.detail


def test_duplicate_gold_assertion_key_rejected_by_loader(tmp_path):
    """ENFORCED: (query_id, revision_id, reviewer_id, start, end) is unique."""
    document = _gold_document()
    document["events"].append(dict(document["events"][0]))
    path = _write(tmp_path, "human-gold.json", document)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(path)
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_INVALID"
    assert "duplicate gold event" in excinfo.value.detail


def test_duplicate_reviewer_set_per_assertion_rejected_by_builder(tmp_path):
    """ENFORCED in ``build_gold_events``: two rows, same reviewer, same assertion."""
    queries = _built_queries()
    events = [_gold_event("q_eval_appearance_0", "reviewer_a"),
              _gold_event("q_eval_appearance_0", "reviewer_a", grade=1)]
    with pytest.raises(ValueError, match="exactly two distinct reviewers required per assertion"):
        labels.build_gold_events(events, queries, "human-gold-v1")


def test_duplicate_gold_reviewer_is_also_refused_end_to_end(tmp_path):
    """ENFORCED (ordering matters): the loader's duplicate key fires first."""
    document = _gold_document()
    document["events"][1] = dict(document["events"][0])  # same reviewer, same coords
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(_write(tmp_path, "human-gold.json", document))
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_INVALID"


def test_gold_identity_representation_variant_is_refused_by_builder(tmp_path):
    """CHARACTERIZATION: pre-existing loader asymmetry, unchanged by the fix.

    ``execution.load_human_gold`` is frozen and still keys rationals by raw
    shape, so it accepts the *same* assertion expressed once as ``[0, 1]`` and
    once as ``{"numerator": 0, "denominator": 1}``.  This test documents that
    loader behaviour; it is NOT one of the two tests that failed before the
    ``labels.build_gold_events`` fix (see ``labels-fix-red.log``).  The builder
    does now reduce both shapes to one exact rational identity, so the duplicate
    reviewer set is refused rather than silently passing as one assertion.
    """
    events = [
        _gold_event("q_eval_appearance_0", "reviewer_a", start=[0, 1], end=[2, 1]),
        _gold_event("q_eval_appearance_0", "reviewer_a",
                    start={"numerator": 0, "denominator": 1},
                    end={"numerator": 2, "denominator": 1}),
    ]
    rows = execution.load_human_gold(
        _write(tmp_path, "human-gold.json", _gold_document(events)))
    assert len(rows) == 2  # loader-level gap: execution.py is frozen/out of scope
    assert rows[0]["start"] != rows[1]["start"]
    with pytest.raises(ValueError, match="exactly two distinct reviewers required per assertion"):
        labels.build_gold_events(events, _built_queries(), "human-gold-v1")


# ---------------------------------------------------------------------------
# 5. malformed gold records -- fail closed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("corruption, reason", [
    (lambda event: event.__setitem__("evidence_class", "SYNTHETIC_FIXTURE"),
     "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN"),
    (lambda event: event.__setitem__("evidence_class", "NOT_OBSERVED"),
     "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN"),
    (lambda event: event.__setitem__("review_status", "MAYBE"),
     "AUTHORIZED_HUMAN_GOLD_REVIEW_STATUS_UNKNOWN"),
    (lambda event: event.__setitem__("time_domain", "NOMINAL_FPS"),
     "AUTHORIZED_HUMAN_GOLD_TIME_DOMAIN_UNKNOWN"),
    (lambda event: event.__delitem__("uncertainty"),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda event: event.__setitem__("grade", 3),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
])
def test_malformed_gold_record_rejected_by_loader(corruption, reason, tmp_path):
    """ENFORCED: closed gold vocabularies and required audit fields fail closed."""
    document = _gold_document()
    corruption(document["events"][0])
    path = _write(tmp_path, "human-gold.json", document)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(path)
    assert excinfo.value.reason == reason


def test_missing_uncertainty_reason_detail_and_builder_surface(tmp_path):
    """ENFORCED: missing uncertainty is named by the loader and the builder."""
    document = _gold_document()
    del document["events"][0]["uncertainty"]
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(_write(tmp_path, "human-gold.json", document))
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_INVALID"
    assert "missing ['uncertainty']" in excinfo.value.detail
    # Same defect seen through the frozen builder's typed reason.
    events = [_gold_event("q_eval_appearance_0", "reviewer_a"),
              _gold_event("q_eval_appearance_0", "reviewer_b")]
    for event in events:
        del event["uncertainty"]
    with pytest.raises(ValueError, match="GOLD_UNCERTAINTY_NOT_DECLARED"):
        labels.build_gold_events(events, _built_queries(), "human-gold-v1")


def test_float_uncertainty_component_rejected_by_loader_and_builder(tmp_path):
    """ENFORCED: no binary float may enter exact-rational uncertainty evidence."""
    document = _gold_document()
    document["events"][0]["uncertainty"] = {
        "start": {"numerator": 0.5, "denominator": 1},
        "end": {"numerator": 2, "denominator": 1},
    }
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(_write(tmp_path, "human-gold.json", document))
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_INVALID"
    assert "components must be integers" in excinfo.value.detail

    events = [_gold_event("q_eval_appearance_0", "reviewer_a"),
              _gold_event("q_eval_appearance_0", "reviewer_b")]
    for event in events:
        event["uncertainty"] = {"start": {"numerator": 0.5, "denominator": 1},
                                "end": {"numerator": 2, "denominator": 1}}
    with pytest.raises(ValueError, match="GOLD_UNCERTAINTY_INVALID"):
        labels.build_gold_events(events, _built_queries(), "human-gold-v1")


def test_grade_three_rejected_by_loader_and_builder(tmp_path):
    """ENFORCED: grade vocabulary is {0, 1, 2} at both surfaces."""
    document = _gold_document()
    document["events"][0]["grade"] = 3
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(_write(tmp_path, "human-gold.json", document))
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_INVALID"
    assert "grade 3" in excinfo.value.detail

    events = [_gold_event("q_eval_appearance_0", "reviewer_a", grade=3),
              _gold_event("q_eval_appearance_0", "reviewer_b", grade=3)]
    with pytest.raises(ValueError, match="invalid grade"):
        labels.build_gold_events(events, _built_queries(), "human-gold-v1")


def test_third_reviewer_for_one_assertion_loader_accepts_builder_rejects(tmp_path):
    """ENFORCED by the builder; the loader deliberately defers the join rule.

    Characterization: exactly three rows on the same assertion load fine, then
    ``build_gold_events`` refuses because an assertion carries exactly two
    distinct reviewers.
    """
    events = [_gold_event("q_eval_appearance_0", f"reviewer_{suffix}")
              for suffix in ("a", "b", "c")]
    rows = execution.load_human_gold(
        _write(tmp_path, "human-gold.json", _gold_document(events)))
    assert len(rows) == 3

    with pytest.raises(ValueError, match="exactly two distinct reviewers required per assertion"):
        _prepare(tmp_path, gold=_gold_document(events))


def test_inconsistent_adjudication_rejected_and_consistent_accepted(tmp_path):
    """ENFORCED: reviewer disagreement needs one consistent adjudication."""
    inconsistent = _gold_document([
        _gold_event("q_eval_appearance_0", "reviewer_a", grade=2,
                    adjudication_ref="adjudication_round_1", adjudicated_grade=2),
        _gold_event("q_eval_appearance_0", "reviewer_b", grade=0,
                    adjudication_ref="adjudication_round_2", adjudicated_grade=2),
    ])
    # The loader accepts the fields (they are individually well formed) ...
    loaded = execution.load_human_gold(
        _write(tmp_path, "inconsistent.json", inconsistent))
    assert {row["adjudication_ref"] for row in loaded} == {
        "adjudication_round_1", "adjudication_round_2"}
    # ... but the join/consistency rule refuses the assertion.
    with pytest.raises(ValueError, match="reviewer disagreement requires consistent adjudication"):
        _prepare(tmp_path, gold=inconsistent)

    consistent = _gold_document([
        _gold_event("q_eval_appearance_0", "reviewer_a", grade=2,
                    adjudication_ref="adjudication_round_1", adjudicated_grade=2),
        _gold_event("q_eval_appearance_0", "reviewer_b", grade=0,
                    adjudication_ref="adjudication_round_1", adjudicated_grade=2),
    ])
    projection = _prepare(tmp_path, gold=consistent)
    assert len(projection["gold_events"]) == 2
    assert {row["payload"]["adjudication_ref"] for row in projection["gold_events"]} == {
        "adjudication_round_1"}


def test_reviewer_disagreement_without_adjudication_rejected(tmp_path):
    """ENFORCED: disagreement with no adjudication cannot be resolved."""
    document = _gold_document([
        _gold_event("q_eval_appearance_0", "reviewer_a", grade=2),
        _gold_event("q_eval_appearance_0", "reviewer_b", grade=0),
    ])
    with pytest.raises(ValueError, match="reviewer disagreement requires consistent adjudication"):
        _prepare(tmp_path, gold=document)


# ---------------------------------------------------------------------------
# 6. reviewer-label isolation: gold never enters the ranker projection
# ---------------------------------------------------------------------------

def _all_keys(value) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(value)
        for item in value.values():
            keys |= _all_keys(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            keys |= _all_keys(item)
    return keys


def test_prepare_projection_has_exact_keys_and_no_label_leakage(tmp_path):
    """ENFORCED: the ranker projection is structurally label-free."""
    projection = _prepare(tmp_path)
    assert set(projection) == {"queries", "gold_events", "ranker_inputs",
                               "gold_excluded_from_ranker"}
    assert projection["gold_excluded_from_ranker"] is True
    assert len(projection["queries"]) == 40
    assert len(projection["gold_events"]) == 4

    ranker = projection["ranker_inputs"]
    assert set(ranker) == {"queries"}
    assert len(ranker["queries"]) == 40
    for row in ranker["queries"]:
        assert set(row) == {"query_id", "text", "query_version", "query_version_digest"}

    forbidden = {"grade", "rationale", "reviewer_id", "reviewer", "family",
                 "presence", "gold", "gold_events", "adjudication_ref",
                 "adjudicated_grade", "evidence_class"}
    assert _all_keys(ranker) & forbidden == set()
    assert "gold" not in json.dumps(ranker)
    json.dumps(projection)  # the whole projection stays JSON-serializable


# ---------------------------------------------------------------------------
# 7. synthetic-label fallback absence
# ---------------------------------------------------------------------------

def test_empty_gold_event_set_rejected_by_loader_and_builder(tmp_path):
    """ENFORCED: an empty gold document never silently means "no labels"."""
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(_write(tmp_path, "empty.json",
                                         {"schema_version": HUMAN_GOLD_SCHEMA,
                                          "label_version": "v1", "events": []}))
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_INVALID"
    assert "non-empty" in excinfo.value.detail

    with pytest.raises(ValueError, match="gold event set cannot be empty"):
        labels.build_gold_events([], _built_queries(), "human-gold-v1")


def test_gold_authenticity_is_not_observed_and_defaults_to_visually_observed(tmp_path):
    """GAP (NOT_OBSERVED): the loader is provenance-blind; the builder defaults.

    The human-gold schema has no provenance/authenticity field and the closed
    evidence vocabulary excludes a synthetic marker (``SYNTHETIC_FIXTURE`` is
    refused).  Yet a row that simply omits ``evidence_class`` is emitted as
    ``VISUALLY_OBSERVED`` by ``build_gold_events``: a synthetic/absent-origin
    row is indistinguishable from authentic human gold and silently acquires an
    observation class.  Authenticity is NOT_OBSERVED here; no authenticity check
    is invented.
    """
    # An explicit synthetic provenance marker is not even a legal value.
    marker = _gold_document()
    marker["events"][0]["evidence_class"] = "SYNTHETIC_FIXTURE"
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(_write(tmp_path, "marker.json", marker))
    assert excinfo.value.reason == "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN"

    # Omitting the field is accepted and defaults to an observed class.
    projection = _prepare(tmp_path)
    assert {row["payload"]["evidence_class"] for row in projection["gold_events"]} == {
        "VISUALLY_OBSERVED"}
    # No provenance field exists on the typed projection to contradict it.
    assert "provenance" not in _all_keys(projection["gold_events"])
    assert "authentic" not in json.dumps(projection["gold_events"]).lower()


# ---------------------------------------------------------------------------
# 8. duplicate editor query TEXT / AI-rewritten text: provenance-blind
# ---------------------------------------------------------------------------

def test_duplicate_editor_query_text_accepted_gap(tmp_path):
    """GAP (NOT_ENFORCED): two distinct query_ids may carry identical text.

    Neither the loader nor ``build_queries`` checks text uniqueness, so the
    same wording can be scored twice under different identities.  The per-query
    version digest still differs because it includes ``query_id``, so the
    duplication is invisible in the digests as well.
    """
    document = _queries_document()
    first, second = document["queries"][0], document["queries"][1]
    second["text"] = first["text"]
    rows = execution.load_editor_queries(
        _write(tmp_path, "editor-queries.json", document))
    assert len(rows) == 40
    assert sum(row["text"] == first["text"] for row in rows) == 2

    projection = _prepare(tmp_path, queries=document)
    payloads = [row["payload"] for row in projection["queries"]]
    duplicates = [row for row in payloads if row["text"] == first["text"]]
    assert {row["query_id"] for row in duplicates} == {first["query_id"],
                                                       second["query_id"]}
    assert len({row["query_version_digest"] for row in duplicates}) == 2


def test_editor_query_provenance_is_structurally_unobservable(tmp_path):
    """GAP (NOT_OBSERVED): the editor-query schema carries no authorship claim.

    ``EDITOR_QUERY_FIELDS`` is exactly five closed fields: no ``editor_id``,
    ``authored_by``, ``provenance`` or rewritten/AI marker.  Software cannot
    authenticate editor authorship from text alone, and any attempt to declare
    it is refused as an unknown field, so authenticity is NOT_OBSERVED.  The
    free-form ``query_version`` is likewise only a caller-declared label.
    """
    assert execution.EDITOR_QUERY_FIELDS == frozenset(
        {"query_id", "text", "family", "presence", "split"})
    assert not (execution.EDITOR_QUERY_FIELDS &
                {"editor_id", "authored_by", "provenance", "author",
                 "ai_rewritten", "rewrite_source"})

    for field in ("editor_id", "authored_by", "ai_rewritten"):
        document = _queries_document()
        document["queries"][0][field] = "claim"
        with pytest.raises(AuthorizedLocalError) as excinfo:
            execution.load_editor_queries(
                _write(tmp_path, "editor-queries.json", document))
        assert excinfo.value.reason == "AUTHORIZED_EDITOR_QUERIES_INVALID"

    # A caller-declared authenticity-sounding query_version is accepted verbatim.
    declared = _prepare(tmp_path, queries=_queries_document(
        query_version="human-editor-authenticated-v1"))
    versions = {row["payload"]["query_version"] for row in declared["queries"]}
    assert versions == {"human-editor-authenticated-v1"}


# ---------------------------------------------------------------------------
# 9. editor-as-reviewer leakage: structurally unobservable, observable part
#     is that reviewer identity comes only from gold rows
# ---------------------------------------------------------------------------

def test_editor_as_reviewer_leakage_is_structurally_unobservable(tmp_path):
    """GAP (NOT_OBSERVED): no editor identity exists to compare reviewers with.

    Editor queries declare no editor id and the authorization declaration has
    no reviewer-roster binding, so "reviewer is also an editor" cannot be
    observed.  The observable invariant is narrower: reviewer ids come only
    from the gold rows and each assertion must carry exactly two distinct ids.
    """
    projection = _prepare(tmp_path)
    reviewers = {row["payload"]["reviewer_id"] for row in projection["gold_events"]}
    assert reviewers == {"reviewer_a", "reviewer_b"}
    assert len(reviewers) == 2
    # Reviewer identity is copied verbatim from the gold document, not derived.
    gold = _gold_document()
    expected = {event["reviewer_id"] for event in gold["events"]}
    assert reviewers == expected

    # A reviewer id equal to an editor query id is accepted: there is no
    # cross-role identity check because the editor side has no comparable id.
    no_cross_check = _gold_document([
        _gold_event("q_eval_appearance_0", "q_eval_appearance_0"),
        _gold_event("q_eval_appearance_0", "reviewer_b"),
    ])
    accepted = _prepare(tmp_path, gold=no_cross_check)
    assert {row["payload"]["reviewer_id"] for row in accepted["gold_events"]} == {
        "q_eval_appearance_0", "reviewer_b"}


# ---------------------------------------------------------------------------
# 10. additional real gaps found by characterization
# ---------------------------------------------------------------------------

def test_mapping_form_distinct_intervals_are_not_conflated():
    """FIXED (narrow guard): mapping-form coordinates keep distinct identities.

    ``build_gold_events`` previously grouped with ``tuple(event.get("start", ()))``;
    for the canonical mapping rational that tuple is the *keys*
    ``("numerator", "denominator")``, so two different intervals for the same
    query/revision reviewed by one person each were merged into a false
    two-reviewer assertion.  That reviewer-independence bypass is now refused.
    """
    events = [
        _gold_event("q_eval_appearance_0", "reviewer_a",
                    start={"numerator": 0, "denominator": 1},
                    end={"numerator": 2, "denominator": 1}),
        _gold_event("q_eval_appearance_0", "reviewer_b",
                    start={"numerator": 10, "denominator": 1},
                    end={"numerator": 12, "denominator": 1}),
    ]
    with pytest.raises(ValueError, match="exactly two distinct reviewers required per assertion"):
        labels.build_gold_events(events, _built_queries(), "human-gold-v1")


def test_mapping_form_two_valid_assertions_are_accepted(tmp_path):
    """FIXED (narrow guard): valid mapping-form assertions are no longer merged.

    Two correctly-formed two-reviewer assertions on the same query/revision,
    both in canonical mapping form, previously collapsed into one four-row
    group and were falsely rejected.  Each assertion now keeps its own identity.
    """
    events = []
    for start_numerator, end_numerator in ((0, 2), (10, 12)):
        for reviewer_id in ("reviewer_a", "reviewer_b"):
            events.append(_gold_event(
                "q_eval_appearance_0", reviewer_id,
                start={"numerator": start_numerator, "denominator": 1},
                end={"numerator": end_numerator, "denominator": 1}))
    loaded = execution.load_human_gold(
        _write(tmp_path, "human-gold.json", _gold_document(events)))
    assert len(loaded) == 4
    projection = _prepare(tmp_path, gold=_gold_document(events))
    emitted = projection["gold_events"]
    assert len(emitted) == 4
    intervals = {(row["payload"]["start"]["numerator"],
                  row["payload"]["end"]["numerator"]) for row in emitted}
    assert intervals == {(0, 2), (10, 12)}


def test_interval_and_uncertainty_coherence_not_enforced_gap(tmp_path):
    """GAP (NOT_ENFORCED): no coherence check on interval/uncertainty endpoints.

    An inverted, half-open interval (start 9 -> end 1) whose declared
    uncertainty (0 -> 2) is disjoint from it is accepted by both the loader and
    the builder; ``_declared_uncertainty`` only reduces endpoints to exact
    rationals and never relates them to ``start``/``end``.
    """
    document = _gold_document([
        _gold_event("q_eval_appearance_0", reviewer_id, start=[9, 1], end=[1, 1])
        for reviewer_id in ("reviewer_a", "reviewer_b")
    ])
    projection = _prepare(tmp_path, gold=document)
    assert len(projection["gold_events"]) == 2
    for row in projection["gold_events"]:
        payload = row["payload"]
        assert payload["start"] == {"numerator": 9, "denominator": 1}
        assert payload["end"] == {"numerator": 1, "denominator": 1}
        assert payload["uncertainty"] == {
            "start": {"numerator": 0, "denominator": 1},
            "end": {"numerator": 2, "denominator": 1},
        }


def test_equivalent_coordinate_shapes_share_interval_identity(tmp_path):
    """Review follow-up F6: reduced interval identity is coordinate-shape independent.

    After the grouping fix, the same assertion expressed once as a 2-sequence
    and once as the canonical mapping is one reviewer-independence group; its
    derived ``interval_id`` must also be one identity, not one per raw shape.
    """
    events = [
        _gold_event("q_eval_appearance_0", "reviewer_a", start=[0, 1], end=[2, 1]),
        _gold_event("q_eval_appearance_0", "reviewer_b",
                    start={"numerator": 0, "denominator": 1},
                    end={"numerator": 2, "denominator": 1}),
    ]
    projection = _prepare(tmp_path, gold=_gold_document(events))
    rows = projection["gold_events"]
    assert len(rows) == 2
    assert len({row["payload"]["interval_id"] for row in rows}) == 1
