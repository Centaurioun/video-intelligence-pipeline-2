import pytest
from gate0.labels import build_gold_events, build_queries, label_version_digest, ranking_inputs
from gate0.split import freeze_relation_split, relation_components

def test_transitive_relation_components_are_source_disjoint_and_deterministic():
    edges = [("r3", "r2"), ("r1", "r2"), ("r5", "r6")]
    components = relation_components(["r1", "r2", "r3", "r4", "r5", "r6"], edges)
    assert components == (("r1", "r2", "r3"), ("r4",), ("r5", "r6"))
    manifest = freeze_relation_split(["r1", "r2", "r3", "r4", "r5", "r6"], edges, "a" * 64, evaluation_components=("r1",), development_components=("r4", "r5"))
    assert {row["payload"]["allocation"] for row in manifest} == {"DEVELOPMENT", "EVALUATION"}
    assert all(row["payload"]["leakage_status"] == "VALID" for row in manifest)

def test_split_rejects_cross_split_relation_after_freeze():
    with pytest.raises(ValueError, match="LEAKAGE_DETECTED"):
        freeze_relation_split(["r1", "r2"], [("r1", "r2")], "b" * 64, evaluation_components=("r1",), development_components=("r2",))

def test_queries_have_exact_32_evaluation_and_8_development_cardinality():
    specs = [(f"q{i}", f"query {i}", ("APPEARANCE", "POSITIVE")) for i in range(24)] + [(f"a{i}", f"absent {i}", ("VISIBLE_ACTION", "ABSENT")) for i in range(8)] + [(f"d{i}", f"dev {i}", ("INTERACTION", "POSITIVE")) for i in range(8)]
    split_by_id = {f"q{i}": "EVALUATION" for i in range(24)} | {f"a{i}": "EVALUATION" for i in range(8)} | {f"d{i}": "DEVELOPMENT" for i in range(8)}
    rows = build_queries(specs, split_by_id, query_version="q-v1")
    assert len(rows) == 40
    assert sum(row["payload"]["split"] == "EVALUATION" for row in rows) == 32
    assert sum(row["payload"]["split"] == "DEVELOPMENT" for row in rows) == 8
    assert sum(row["payload"]["presence"] == "POSITIVE" and row["payload"]["split"] == "EVALUATION" for row in rows) == 24

def test_gold_join_is_typed_and_ranking_inputs_are_blinded():
    specs = [(f"q{i}", f"query {i}", ("APPEARANCE", "POSITIVE")) for i in range(24)] + [(f"a{i}", f"absent {i}", ("VISIBLE_ACTION", "ABSENT")) for i in range(8)] + [(f"d{i}", f"dev {i}", ("INTERACTION", "POSITIVE")) for i in range(8)]
    queries = build_queries(specs, {**{f"q{i}": "EVALUATION" for i in range(24)}, **{f"a{i}": "EVALUATION" for i in range(8)}, **{f"d{i}": "DEVELOPMENT" for i in range(8)}}, "q-v1")
    gold = build_gold_events([{"query_id": "q0", "revision_id": "r1", "reviewer_id": "u1", "grade": 2, "rationale": "visible", "stream_index": 0, "start": (0, 1), "end": (1, 1), "uncertainty": {"start": {"numerator": 0, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}}}, {"query_id": "q0", "revision_id": "r1", "reviewer_id": "u2", "grade": 2, "rationale": "visible", "stream_index": 0, "start": (0, 1), "end": (1, 1), "uncertainty": {"start": {"numerator": 0, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}}}], queries, "gold-v1")
    assert gold[0]["payload"]["query_id"] == "q0"
    assert "gold_events" not in ranking_inputs(queries)
    with pytest.raises(ValueError, match="reviewer"):
        build_gold_events([{"query_id": "q0", "revision_id": "r1", "grade": 2}], queries, "gold-v1")

def test_label_version_changes_when_query_or_gold_changes():
    assert label_version_digest([{"query_id": "q1", "text": "a"}]) != label_version_digest([{"query_id": "q1", "text": "b"}])


def _full_queries():
    specs = [(f"q{i}", f"query {i}", ("APPEARANCE", "POSITIVE")) for i in range(24)] + [(f"a{i}", f"absent {i}", ("VISIBLE_ACTION", "ABSENT")) for i in range(8)] + [(f"d{i}", f"dev {i}", ("INTERACTION", "POSITIVE")) for i in range(8)]
    split = {**{f"q{i}": "EVALUATION" for i in range(24)}, **{f"a{i}": "EVALUATION" for i in range(8)}, **{f"d{i}": "DEVELOPMENT" for i in range(8)}}
    return build_queries(specs, split, "q-v1")

def test_post_freeze_cross_split_relation_invalidates_without_mutating_version():
    from gate0.split import validate_post_freeze_relations
    rows = freeze_relation_split(["r1", "r2", "r3"], [("r1", "r2")], "c" * 64, evaluation_components=("r1",), development_components=("r3",))
    members = {row["payload"]["relation_component_id"]: ("r1", "r2") if row["payload"]["allocation"] == "EVALUATION" else ("r3",) for row in rows}
    result = validate_post_freeze_relations(rows, members, [("r2", "r3")])
    assert not result.valid and result.requires_new_version and result.split_version == "split-v1"
    assert all(row["payload"]["leakage_status"] == "VALID" for row in rows)

def test_gold_requires_exactly_two_reviewers_per_typed_assertion_and_adjudication():
    queries = _full_queries()
    event = {"query_id": "q0", "revision_id": "r1", "grade": 2, "rationale": "visible", "stream_index": 0, "start": (0, 1), "end": (1, 1), "uncertainty": {"start": {"numerator": 0, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}}}
    with pytest.raises(ValueError, match="exactly two"):
        build_gold_events([dict(event, reviewer_id="u1")], queries, "gold-v1")
    with pytest.raises(ValueError, match="agreement|adjudication"):
        build_gold_events([dict(event, reviewer_id="u1"), dict(event, reviewer_id="u2", grade=1)], queries, "gold-v1")
    rows = build_gold_events([dict(event, reviewer_id="u1"), dict(event, reviewer_id="u2")], queries, "gold-v1")
    assert len(rows) == 2

def test_ranking_projection_contains_only_query_execution_fields():
    projected = ranking_inputs(_full_queries())
    assert set(projected) == {"queries"}
    assert set(projected["queries"][0]) == {"query_id", "text", "query_version", "query_version_digest"}
    assert not any(key in projected["queries"][0] for key in ("presence", "family", "split", "gold_events"))

# --- Gate-0 contract correction (Wave 2): declared exact-rational uncertainty + canonical time domain ---

CANONICAL_TIME_DOMAINS = (
    "SEMANTIC_SECONDS",
    "TECHNICAL_WINDOW",
    "MATCHED_OFFSET",
    "SOURCE_PTS",
    "SOURCE_FRAME",
    "PROXY_TIME",
    "TIMELINE_TIME",
    "RENDERED_OUTPUT",
)


def _declared_uncertainty(start=0, end=0):
    return {"start": {"numerator": start, "denominator": 1}, "end": {"numerator": end, "denominator": 1}}


def _gold_event(reviewer_id, *, start=(0, 1), end=(4, 1), uncertainty=None, **overrides):
    event = {
        "query_id": "q0",
        "revision_id": "r1",
        "reviewer_id": reviewer_id,
        "grade": 2,
        "rationale": "visible",
        "stream_index": 0,
        "start": start,
        "end": end,
        "uncertainty": _declared_uncertainty() if uncertainty is None else uncertainty,
    }
    event.update(overrides)
    return event


def _gold_pair(*, start=(0, 1), end=(4, 1), uncertainty=None, **overrides):
    return [_gold_event("u1", start=start, end=end, uncertainty=uncertainty, **overrides),
            _gold_event("u2", start=start, end=end, uncertainty=uncertainty, **overrides)]


def _only_issue(gold):
    assert len(gold) == 2
    assert {row["payload"]["reviewer_id"] for row in gold} == {"u1", "u2"}
    return gold[0]["payload"]


def test_gold_event_persists_declared_uncertainty_as_reduced_exact_rationals():
    gold = build_gold_events(
        _gold_pair(uncertainty={"start": {"numerator": 2, "denominator": 4}, "end": {"numerator": 6, "denominator": 3}}),
        _full_queries(),
        "gold-v1",
    )
    payload = _only_issue(gold)
    assert payload["uncertainty"] == {
        "start": {"numerator": 1, "denominator": 2},
        "end": {"numerator": 2, "denominator": 1},
    }
    assert set(payload["uncertainty"]) == {"start", "end"}
    for endpoint in payload["uncertainty"].values():
        assert set(endpoint) == {"numerator", "denominator"}
        assert isinstance(endpoint["numerator"], int) and isinstance(endpoint["denominator"], int)
    assert payload["uncertainty"]["start"]["denominator"] > 0
    assert payload["uncertainty"]["end"]["denominator"] > 0


def test_gold_event_uncertainty_accepts_lower_upper_shape_without_float():
    gold = build_gold_events(
        _gold_pair(uncertainty={"lower": {"numerator": 1, "denominator": 3}, "upper": (7, 6)}),
        _full_queries(),
        "gold-v1",
    )
    payload = _only_issue(gold)
    assert payload["uncertainty"] == {
        "start": {"numerator": 1, "denominator": 3},
        "end": {"numerator": 7, "denominator": 6},
    }


def test_gold_event_uncertainty_normalizes_negative_denominators():
    gold = build_gold_events(
        _gold_pair(uncertainty={"start": {"numerator": -1, "denominator": -3}, "end": {"numerator": 1, "denominator": -2}}),
        _full_queries(),
        "gold-v1",
    )
    payload = _only_issue(gold)
    assert payload["uncertainty"] == {
        "start": {"numerator": 1, "denominator": 3},
        "end": {"numerator": -1, "denominator": 2},
    }


def test_gold_event_without_declared_uncertainty_fails_closed():
    events = _gold_pair()
    for event in events:
        del event["uncertainty"]
    with pytest.raises(ValueError, match="GOLD_UNCERTAINTY_NOT_DECLARED"):
        build_gold_events(events, _full_queries(), "gold-v1")


@pytest.mark.parametrize(
    "uncertainty",
    [
        {"start": {"numerator": 0.5, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}},
        {"start": {"numerator": True, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}},
        {"start": {"numerator": 1, "denominator": 0}, "end": {"numerator": 0, "denominator": 1}},
        {"left": {"numerator": 0, "denominator": 1}, "right": {"numerator": 0, "denominator": 1}},
        {"start": (1, 2, 3), "end": {"numerator": 0, "denominator": 1}},
    ],
)
def test_gold_event_rejects_non_exact_uncertainty(uncertainty):
    with pytest.raises(ValueError, match="GOLD_UNCERTAINTY_INVALID"):
        build_gold_events(_gold_pair(uncertainty=uncertainty), _full_queries(), "gold-v1")


def test_gold_time_domain_defaults_to_canonical_semantic_seconds():
    payload = _only_issue(build_gold_events(_gold_pair(), _full_queries(), "gold-v1"))
    assert payload["time_domain"] == "SEMANTIC_SECONDS"


@pytest.mark.parametrize("domain", CANONICAL_TIME_DOMAINS)
def test_gold_time_domain_honors_explicit_canonical_domain(domain):
    payload = _only_issue(build_gold_events(_gold_pair(time_domain=domain), _full_queries(), "gold-v1"))
    assert payload["time_domain"] == domain


@pytest.mark.parametrize("domain", ["NORMALIZED_PTS", "semantic_seconds", "UNKNOWN_DOMAIN"])
def test_gold_time_domain_fails_closed_on_non_canonical_domain(domain):
    with pytest.raises(ValueError, match="GOLD_TIME_DOMAIN_NOT_CANONICAL"):
        build_gold_events(_gold_pair(time_domain=domain), _full_queries(), "gold-v1")


def test_gold_payload_stays_closed_apart_from_uncertainty():
    payload = _only_issue(build_gold_events(_gold_pair(), _full_queries(), "gold-v1"))
    assert set(payload) == {
        "assertion_id", "interval_id", "query_id", "revision_id", "reviewer_id", "grade",
        "rationale", "label_version", "review_status", "evidence_class", "stream_index",
        "time_domain", "origin", "start", "end", "time_base", "endpoint_semantics",
        "precision", "producer_attempt_id", "refinement_eligibility", "uncertainty",
    }
