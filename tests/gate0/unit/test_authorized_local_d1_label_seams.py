"""D-1 Lane A / S3: editor-query and human-gold preparation seams.

These seams load the *future* real-corpus label inputs without ever treating
synthetic labels as authentic truth and without leaking gold/human judgments
into the ranker.  The frozen cardinality/consistency rules stay in
``gate0.labels``: the seam only builds typed projections and lets the frozen
builders' ``ValueError`` surfaces.

No declared source path is opened/stat'ed, and no reviewer judgement is
fabricated here.
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path

import pytest
from gate0 import execution
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


def _queries_document(*, query_version: str = "editor-v1", text_suffix: str = "") -> dict:
    queries = []
    for family in FAMILIES:
        for index in range(6):
            queries.append({
                "query_id": f"q_eval_{family.lower()}_{index}",
                "text": f"editor query {family} {index}{text_suffix}",
                "family": family,
                "presence": "POSITIVE",
                "split": "EVALUATION",
            })
    for index in range(8):
        queries.append({
            "query_id": f"q_eval_absent_{index}",
            "text": f"editor absent query {index}{text_suffix}",
            "family": FAMILIES[index % 4],
            "presence": "ABSENT",
            "split": "EVALUATION",
        })
    for index in range(8):
        queries.append({
            "query_id": f"q_dev_{index}",
            "text": f"editor development query {index}{text_suffix}",
            "family": FAMILIES[index % 4],
            "presence": "POSITIVE",
            "split": "DEVELOPMENT",
        })
    return {"schema_version": EDITOR_QUERIES_SCHEMA, "query_version": query_version,
            "queries": queries}


def _gold_event(query_id: str, reviewer_id: str, *, grade: int = 2,
                revision_id: str = "rev_eval_alpha") -> dict:
    return {
        "query_id": query_id,
        "revision_id": revision_id,
        "reviewer_id": reviewer_id,
        "grade": grade,
        "rationale": f"human rationale from {reviewer_id}",
        "stream_index": 0,
        "start": (0, 1),
        "end": (2, 1),
        "uncertainty": {
            "start": {"numerator": 0, "denominator": 1},
            "end": {"numerator": 2, "denominator": 1},
        },
    }


def _gold_document() -> dict:
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
            {"revision_id": "rev_eval_beta", "occurrence_id": "occ_eval_beta",
             "content_id": "content_eval_beta", "locator": "media/beta.mp4",
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
        "evaluation_revision_ids": ["rev_eval_alpha", "rev_eval_beta"],
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


def _install_source_guard(monkeypatch, sentinel: Path) -> None:
    prefix = str(sentinel) + os.sep
    for name in ("stat", "lstat", "open"):
        real = getattr(os, name)

        def guarded(path, *args, __real=real, __prefix=prefix, __name=name, **kwargs):
            if str(path).startswith(__prefix):
                raise AssertionError(f"forbidden declared-source {__name}: {path}")
            return __real(path, *args, **kwargs)

        monkeypatch.setattr(os, name, guarded)
    real_io_open = io.open

    def guarded_io_open(file, *args, **kwargs):
        if str(file).startswith(prefix):
            raise AssertionError(f"forbidden declared-source open: {file}")
        return real_io_open(file, *args, **kwargs)

    monkeypatch.setattr(io, "open", guarded_io_open)


# ---------------------------------------------------------------------------
# editor-query loader
# ---------------------------------------------------------------------------

def test_editor_queries_load_and_normalize(tmp_path):
    path = _write(tmp_path, "editor-queries.json", _queries_document())
    rows = execution.load_editor_queries(path)
    assert len(rows) == 40
    assert all(set(row) == {"query_id", "text", "family", "presence", "split"} for row in rows)
    assert sum(row["split"] == "EVALUATION" for row in rows) == 32
    assert sum(row["split"] == "DEVELOPMENT" for row in rows) == 8


@pytest.mark.parametrize("corruption, reason", [
    (lambda doc: doc.__setitem__("schema_version", "gate0.editor-queries.v2"),
     "AUTHORIZED_EDITOR_QUERIES_SCHEMA_MISMATCH"),
    (lambda doc: doc.__setitem__("queries", "not-a-list"),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
    (lambda doc: doc["queries"][0].__setitem__("family", "NOT_A_FAMILY"),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
    (lambda doc: doc["queries"][0].__setitem__("presence", "MAYBE"),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
    (lambda doc: doc["queries"][0].__setitem__("text", ""),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
    (lambda doc: doc["queries"].append(dict(doc["queries"][0])),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
    (lambda doc: doc["queries"][0].__setitem__("unknown", "x"),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
    (lambda doc: doc.__setitem__("query_version", ""),
     "AUTHORIZED_EDITOR_QUERIES_INVALID"),
])
def test_editor_queries_fail_closed(corruption, reason, tmp_path):
    document = _queries_document()
    corruption(document)
    path = _write(tmp_path, "editor-queries.json", document)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_editor_queries(path)
    assert excinfo.value.reason == reason


# ---------------------------------------------------------------------------
# human-gold loader
# ---------------------------------------------------------------------------

def test_human_gold_loads_declared_rows(tmp_path):
    path = _write(tmp_path, "human-gold.json", _gold_document())
    rows = execution.load_human_gold(path)
    assert len(rows) == 4
    assert {row["reviewer_id"] for row in rows} == {"reviewer_a", "reviewer_b"}
    assert all(row["grade"] == 2 for row in rows)


@pytest.mark.parametrize("corruption, reason", [
    (lambda doc: doc.__setitem__("schema_version", "gate0.human-gold.v2"),
     "AUTHORIZED_HUMAN_GOLD_SCHEMA_MISMATCH"),
    (lambda doc: doc.__setitem__("events", {}),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"].append(dict(doc["events"][0])),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("grade", 3),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("grade", True),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("start", (0.5, 1)),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("uncertainty", {}),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("reviewer_id", ""),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    # S6: optional fields carry the frozen closed vocabularies.
    (lambda doc: doc["events"][0].__setitem__("evidence_class", "AUTHENTIC"),
     "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN"),
    (lambda doc: doc["events"][0].__setitem__("evidence_class", "NOT_OBSERVED"),
     "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN"),
    (lambda doc: doc["events"][0].__setitem__("review_status", "MAYBE"),
     "AUTHORIZED_HUMAN_GOLD_REVIEW_STATUS_UNKNOWN"),
    (lambda doc: doc["events"][0].__setitem__("refinement_eligibility", "MAYBE"),
     "AUTHORIZED_HUMAN_GOLD_REFINEMENT_ELIGIBILITY_UNKNOWN"),
    (lambda doc: doc["events"][0].__setitem__("time_domain", "NOMINAL_FPS"),
     "AUTHORIZED_HUMAN_GOLD_TIME_DOMAIN_UNKNOWN"),
    (lambda doc: doc["events"][0].__setitem__("adjudicated_grade", 3),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("adjudicated_grade", True),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("origin", (0.5, 1)),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("time_base", {"numerator": 1}),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("precision", ""),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("producer_attempt_id", "Not Valid!"),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
    (lambda doc: doc["events"][0].__setitem__("adjudication_ref", "Not Valid!"),
     "AUTHORIZED_HUMAN_GOLD_INVALID"),
])
def test_human_gold_fail_closed(corruption, reason, tmp_path):
    document = _gold_document()
    corruption(document)
    path = _write(tmp_path, "human-gold.json", document)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(path)
    assert excinfo.value.reason == reason


# S8 / F-D1: closed-vocabulary fields must refuse non-string JSON values with the
# canonical reason code, never with a bare ``TypeError`` from set membership.
# ``["MEASURED"]``/``{"a": 1}``/``[]``/``{}`` are valid JSON but unhashable, so a
# raw ``value in frozenset`` raises ``TypeError: unhashable type``; the seam's
# contract is a typed ``AuthorizedLocalError``.
S8_OPTIONAL_VOCABULARY_FIELDS = (
    ("evidence_class", "AUTHORIZED_HUMAN_GOLD_EVIDENCE_CLASS_UNKNOWN"),
    ("review_status", "AUTHORIZED_HUMAN_GOLD_REVIEW_STATUS_UNKNOWN"),
    ("refinement_eligibility", "AUTHORIZED_HUMAN_GOLD_REFINEMENT_ELIGIBILITY_UNKNOWN"),
    ("time_domain", "AUTHORIZED_HUMAN_GOLD_TIME_DOMAIN_UNKNOWN"),
)
S8_NON_STRING_VALUES = (["MEASURED"], {"a": 1}, [], {}, 1.5, None)


@pytest.mark.parametrize("field, reason", S8_OPTIONAL_VOCABULARY_FIELDS)
@pytest.mark.parametrize("value", S8_NON_STRING_VALUES)
def test_gold_optional_vocabulary_fields_refuse_non_strings_without_typeerror(
        field, reason, value, tmp_path):
    document = _gold_document()
    document["events"][0][field] = value
    path = _write(tmp_path, "human-gold.json", document)
    try:
        execution.load_human_gold(path)
    except AuthorizedLocalError as exc:
        assert exc.reason == reason
    except TypeError as exc:  # F-D1: refuse, never crash the seam
        pytest.fail(f"raw TypeError for {field}={value!r}: {exc}")
    else:
        pytest.fail(f"{field}={value!r} was accepted by the closed vocabulary")


# ---------------------------------------------------------------------------
# typed preparation projection, no ranker leakage
# ---------------------------------------------------------------------------

def _prepare(tmp_path, *, queries=None, gold=None, declaration_path=None):
    queries_path = _write(tmp_path, "editor-queries.json", queries or _queries_document())
    gold_path = _write(tmp_path, "human-gold.json", gold or _gold_document())
    declaration = load_authorized_local_declaration(declaration_path or _declaration(tmp_path))
    return execution.prepare_authorized_label_inputs(
        declaration=declaration,
        editor_queries_path=queries_path,
        human_gold_path=gold_path,
    )


def test_prepare_builds_typed_projections_without_gold_leakage(tmp_path):
    projection = _prepare(tmp_path)
    assert projection["gold_excluded_from_ranker"] is True
    assert len(projection["queries"]) == 40
    assert len(projection["gold_events"]) == 4

    payloads = [row["payload"] for row in projection["queries"]]
    assert sum(row["split"] == "EVALUATION" for row in payloads) == 32
    assert sum(row["split"] == "DEVELOPMENT" for row in payloads) == 8
    assert sum(row["split"] == "EVALUATION" and row["presence"] == "POSITIVE"
               for row in payloads) == 24
    for family in FAMILIES:
        assert sum(row["split"] == "EVALUATION" and row["presence"] == "POSITIVE"
                   and row["family"] == family for row in payloads) == 6

    ranker = projection["ranker_inputs"]
    assert set(ranker) == {"queries"}
    assert len(ranker["queries"]) == 40
    for row in ranker["queries"]:
        assert set(row) == {"query_id", "text", "query_version", "query_version_digest"}
    serialized = json.dumps(ranker)
    for forbidden in ("grade", "reviewer", "rationale", "gold"):
        assert forbidden not in serialized
    json.dumps(projection)  # the whole projection is JSON-serializable


def test_prepare_delegates_frozen_query_cardinality(tmp_path):
    short = _queries_document()
    short["queries"] = short["queries"][:-1]
    with pytest.raises(ValueError):
        _prepare(tmp_path, queries=short)

    unbalanced = _queries_document()
    for row in unbalanced["queries"]:
        if row["query_id"] == "q_eval_appearance_0":
            row["presence"] = "ABSENT"
            break
    with pytest.raises(ValueError):
        _prepare(tmp_path, queries=unbalanced)


def test_prepare_delegates_two_reviewer_rule(tmp_path):
    gold = _gold_document()
    gold["events"] = [event for event in gold["events"]
                      if not (event["reviewer_id"] == "reviewer_b"
                              and event["query_id"] == "q_eval_appearance_0")]
    with pytest.raises(ValueError):
        _prepare(tmp_path, gold=gold)


def test_prepare_rejects_gold_on_development_or_unknown_revision(tmp_path):
    development = _gold_document()
    for event in development["events"]:
        event["revision_id"] = "rev_dev_probe"
    with pytest.raises(AuthorizedLocalError) as excinfo:
        _prepare(tmp_path, gold=development)
    assert excinfo.value.reason == "AUTHORIZED_GOLD_REVISION_NOT_EVALUATION"

    unknown = _gold_document()
    for event in unknown["events"]:
        event["revision_id"] = "rev_unknown"
    with pytest.raises(AuthorizedLocalError) as excinfo:
        _prepare(tmp_path, gold=unknown)
    assert excinfo.value.reason == "AUTHORIZED_GOLD_REVISION_UNKNOWN"


def test_edited_query_text_changes_version_digest(tmp_path):
    first = _prepare(tmp_path)
    second = _prepare(tmp_path, queries=_queries_document(text_suffix=" (edited)"))
    digests_first = {row["payload"]["query_id"]: row["payload"]["query_version_digest"]
                     for row in first["queries"]}
    digests_second = {row["payload"]["query_id"]: row["payload"]["query_version_digest"]
                      for row in second["queries"]}
    assert digests_first != digests_second
    assert len(set(digests_first.values())) == 40


def test_label_seams_never_touch_declared_sources(tmp_path, monkeypatch):
    sentinel = tmp_path / "declared-sources"
    sentinel.mkdir()
    _install_source_guard(monkeypatch, sentinel)
    projection = _prepare(tmp_path)
    assert len(projection["queries"]) == 40

# ---------------------------------------------------------------------------
# S6: closed human-gold option vocabularies + label-input size quota
# ---------------------------------------------------------------------------

def test_human_gold_accepts_every_closed_optional_value(tmp_path):
    document = _gold_document()
    document["events"][0].update({
        "evidence_class": "VISUALLY_OBSERVED",
        "review_status": "ACCEPTED",
        "refinement_eligibility": "ELIGIBLE",
        "time_domain": "SOURCE_PTS",
        "adjudicated_grade": 2,
        "adjudication_ref": "adjudication_round_1",
        "origin": {"numerator": 0, "denominator": 1},
        "time_base": {"numerator": 1, "denominator": 1000},
        "precision": "exact rational declared by reviewer",
        "producer_attempt_id": "attempt_reviewer_a_1",
    })
    path = _write(tmp_path, "human-gold.json", document)
    rows = execution.load_human_gold(path)
    first = next(row for row in rows if row["reviewer_id"] == "reviewer_a")
    assert first["evidence_class"] == "VISUALLY_OBSERVED"
    assert first["review_status"] == "ACCEPTED"
    assert first["refinement_eligibility"] == "ELIGIBLE"
    assert first["time_domain"] == "SOURCE_PTS"
    assert first["adjudicated_grade"] == 2
    assert first["adjudication_ref"] == "adjudication_round_1"
    assert first["origin"] == {"numerator": 0, "denominator": 1}
    assert first["time_base"] == {"numerator": 1, "denominator": 1000}
    assert first["precision"] == "exact rational declared by reviewer"
    assert first["producer_attempt_id"] == "attempt_reviewer_a_1"


def test_label_input_size_quota_fails_closed_before_json_parse(tmp_path, monkeypatch):
    pad = "x" * (execution.LABEL_INPUT_MAX_BYTES + 1)
    path = _write(tmp_path, "human-gold-huge.json", {"schema_version": HUMAN_GOLD_SCHEMA,
                                                     "label_version": "v1", "pad": pad})
    size = path.stat().st_size

    def forbidden_loads(*args, **kwargs):
        raise AssertionError("label input over quota must not be parsed")

    monkeypatch.setattr(execution.json, "loads", forbidden_loads)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_human_gold(path)
    assert excinfo.value.reason == "AUTHORIZED_LABEL_INPUT_TOO_LARGE"
    assert excinfo.value.detail == str(size)

    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution.load_editor_queries(path)
    assert excinfo.value.reason == "AUTHORIZED_LABEL_INPUT_TOO_LARGE"


# ---------------------------------------------------------------------------
# S7: prep-time query cardinality (contract A3: 32 eval = 24 positive + 8 absent,
# 6 positives per family, 8 development; GATE_0_EXPERIMENT_CONTRACT.md)
# ---------------------------------------------------------------------------

def _skew_positive_families(*, appearance: int, visible: int) -> dict:
    document = _queries_document()
    kept = [row for row in document["queries"]
            if not (row["split"] == "EVALUATION" and row["presence"] == "POSITIVE"
                    and row["family"] in ("APPEARANCE", "VISIBLE_ACTION"))]
    for family, count in (("APPEARANCE", appearance), ("VISIBLE_ACTION", visible)):
        for index in range(count):
            kept.append({"query_id": f"q_eval_{family.lower()}_{index}",
                         "text": f"editor query {family} {index}", "family": family,
                         "presence": "POSITIVE", "split": "EVALUATION"})
    document["queries"] = kept
    return document


def _cardinality_rows(*, parents_per_family=6, absent=8, development=8) -> list[dict]:
    rows = []
    for family in FAMILIES:
        for index in range(parents_per_family if not isinstance(parents_per_family, dict)
                           else parents_per_family[family]):
            rows.append({"family": family, "presence": "POSITIVE", "split": "EVALUATION"})
    for _ in range(absent):
        rows.append({"family": FAMILIES[0], "presence": "ABSENT", "split": "EVALUATION"})
    for _ in range(development):
        rows.append({"family": FAMILIES[0], "presence": "POSITIVE", "split": "DEVELOPMENT"})
    return rows


def test_prepare_rejects_family_positive_skew(tmp_path):
    document = _skew_positive_families(appearance=7, visible=5)
    with pytest.raises(AuthorizedLocalError) as excinfo:
        _prepare(tmp_path, queries=document)
    assert excinfo.value.reason == "AUTHORIZED_QUERY_CARDINALITY_INVALID"
    assert "APPEARANCE" in excinfo.value.detail or "VISIBLE_ACTION" in excinfo.value.detail


def test_prepare_rejects_absent_and_development_skew(tmp_path):
    absent = _queries_document()
    absent["queries"].append({"query_id": "q_eval_absent_extra", "text": "extra absent",
                              "family": FAMILIES[0], "presence": "ABSENT",
                              "split": "EVALUATION"})
    with pytest.raises(ValueError):
        _prepare(tmp_path, queries=absent)
    development = _queries_document()
    development["queries"].append({"query_id": "q_dev_extra", "text": "extra dev",
                                   "family": FAMILIES[0], "presence": "POSITIVE",
                                   "split": "DEVELOPMENT"})
    with pytest.raises(ValueError):
        _prepare(tmp_path, queries=development)


def test_query_cardinality_guard_reports_precise_counts():
    rows = _cardinality_rows(parents_per_family={
        "APPEARANCE": 7, "VISIBLE_ACTION": 5,
        "INTERACTION": 6, "SCENE_COMPOSITION_CAMERA_MOVEMENT": 6})
    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(rows)
    assert excinfo.value.reason == "AUTHORIZED_QUERY_CARDINALITY_INVALID"
    assert "APPEARANCE POSITIVE 7 != 6" in excinfo.value.detail

    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(_cardinality_rows(absent=9))
    assert "EVALUATION ABSENT 9 != 8" in excinfo.value.detail

    with pytest.raises(AuthorizedLocalError) as excinfo:
        execution._authorized_query_cardinality(_cardinality_rows(development=9))
    assert "DEVELOPMENT 9 != 8" in excinfo.value.detail


def test_query_cardinality_guard_accepts_the_contract_set():
    execution._authorized_query_cardinality(_cardinality_rows())


def test_prepare_accepts_contract_cardinality(tmp_path):
    projection = _prepare(tmp_path)
    payloads = [record["payload"] for record in projection["queries"]]
    assert len(payloads) == 40
    assert sum(p["split"] == "EVALUATION" and p["presence"] == "POSITIVE"
               for p in payloads) == 24
    assert sum(p["split"] == "EVALUATION" and p["presence"] == "ABSENT"
               for p in payloads) == 8
    assert sum(p["split"] == "DEVELOPMENT" for p in payloads) == 8
