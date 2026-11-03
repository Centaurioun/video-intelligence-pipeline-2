import json
from pathlib import Path

import pytest

from gate0.evaluation import evaluate, load_reviewer_input, reviewer_judgments, _input_digest_for, _mapping_digest_for
from gate0.stages.report import decide_gate, report


def _rows():
    rows = []
    families = ("APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT")
    for i in range(24):
        rows.append({"query_id": f"q{i}", "family": families[i // 6], "presence": "POSITIVE"})
    for i in range(8):
        rows.append({"query_id": f"a{i}", "family": "APPEARANCE", "presence": "ABSENT"})
    return rows


def _review_rows(hit=True):
    out = []
    for i in range(24):
        for token, arm in (("arm-a", "metadata-floor"), ("arm-b", "offline-development-arm")):
            grade = 2 if hit else 0
            for reviewer in ("reviewer-1", "reviewer-2"):
                out.append({"assertion_id": f"assertion-{i}", "query_id": f"q{i}", "window_id": f"w{i}", "blind_arm_token": token,
                    "reviewer_id": reviewer, "grade": grade, "ambiguity": "NONE", "review_status": "ACCEPTED",
                    "assertion": {"version": "v1", "text": f"query {i}", "digest": "d" * 64}})
    return out


def _input(tmp_path, rows=None):
    rows = rows if rows is not None else _review_rows()
    token_map = ({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})
    payload = {"schema_version": "gate0.reviewer-input.v1", "input_digest": _input_digest_for("gate0.reviewer-input.v1", rows), "blind_mapping_digest": _mapping_digest_for(token_map),
               "rows": rows}
    path = tmp_path / "judgments.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_reviewer_input_requires_exact_two_tokens_and_two_reviewers(tmp_path):
    path = _input(tmp_path)
    envelope = load_reviewer_input(path, authorized_root=tmp_path, token_map=(
        {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
        {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
    ), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    assert len(envelope.rows) == 96
    assert {row.blind_arm_token for row in envelope.rows} == {"arm-a", "arm-b"}


def test_duplicate_or_unknown_token_is_rejected(tmp_path):
    rows = _review_rows() + [dict(_review_rows()[0], blind_arm_token="arm-c")]
    with pytest.raises(ValueError, match="token|duplicate"):
        load_reviewer_input(_input(tmp_path, rows), authorized_root=tmp_path,
            token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))


def test_metrics_use_fixed_24_denominator_and_decision_precedence(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    result = evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64)
    assert result.metrics["hit_at_10.semantic"].numerator == 24
    assert result.metrics["hit_at_10.semantic"].denominator == 24
    assert result.metrics["paired_lift.semantic_minus_metadata"].numerator == 0
    assert decide_gate(result, validity="VALID", policy_status="ALLOW", repeat_status="EQUAL") == "FAIL"
    assert decide_gate(result, validity="INVALID_PROTOCOL", policy_status="ALLOW", repeat_status="EQUAL") == "INVALID_PROTOCOL"
    assert decide_gate(result, validity="NOT_RUN", policy_status="BLOCKED_PREREQUISITE", repeat_status="NOT_RUN") == "NOT_RUN"
    assert report(result, run_id="run-1", authority="owner", reviewers=("reviewer-1", "reviewer-2"), validity="VALID", policy_status="ALLOW", repeat_status="EQUAL") .gate_decision == "FAIL"


def test_unresolved_review_status_and_tampered_digest_are_rejected(tmp_path):
    rows = _review_rows()
    rows[0] = dict(rows[0], review_status="UNREVIEWED")
    path = _input(tmp_path, rows)
    token_map = ({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})
    envelope = load_reviewer_input(path, authorized_root=tmp_path, token_map=token_map, expected_mapping_digest=_mapping_digest_for(token_map))
    with pytest.raises(ValueError, match="final"):
        reviewer_judgments(envelope, token_map=token_map)


def test_incomplete_family_and_target_coverage_are_rejected(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    with pytest.raises(ValueError, match="24|six"):
        evaluate([row for row in _rows() if row.get("query_id") != "q0"], judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64)
    with pytest.raises(ValueError, match="coverage"):
        evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64, coverage={"planned": 2, "succeeded": 1})


def test_typed_ranked_candidate_and_gold_join_controls_hit(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    candidates = [{"query_id":"q0","window_id":"w0","arm_id":"offline-development-arm","rank":1,"revision_id":"rev-1","start":0,"end":1,"mapping_ref":"map-1","origin":{"numerator":0,"denominator":1},"time_base":{"numerator":1,"denominator":1}}]
    gold = [{"query_id":"q0","window_id":"other","revision_id":"rev-1","grade":2,"start":5,"end":6,"uncertainty":{"start":0,"end":0}}]
    result = evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64, ranked_candidates=candidates, gold_events=gold)
    assert result.per_query["q0"]["semantic"] == 0


def test_missing_mapping_or_uncertainty_evidence_is_invalid(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    candidate = {"query_id":"q0","window_id":"w0","arm_id":"offline-development-arm","rank":1,"revision_id":"rev-1","start":0,"end":1}
    gold = [{"query_id":"q0","revision_id":"rev-1","grade":2,"start":0,"end":1,"uncertainty":{"start":0,"end":0}}]
    with pytest.raises(ValueError, match="mapping"):
        evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64, ranked_candidates=[candidate], gold_events=gold)


@pytest.mark.parametrize("field,value", [("mapping_ref", ""), ("origin", {"numerator": 0}),
                                          ("time_base", {"numerator": 0, "denominator": 1})])
def test_malformed_mapping_origin_or_time_base_is_invalid_protocol(tmp_path, field, value):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    candidate = {"query_id":"q0","window_id":"w0","arm_id":"offline-development-arm","rank":1,"revision_id":"rev-1","start":0,"end":1,"mapping_ref":"map-1","origin":{"numerator":0,"denominator":1},"time_base":{"numerator":1,"denominator":1}}
    candidate[field] = value
    gold = [{"query_id":"q0","revision_id":"rev-1","grade":2,"start":0,"end":1,"uncertainty":{"start":0,"end":0}}]
    with pytest.raises(ValueError, match="protocol|mapping|origin|time-base"):
        evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64, ranked_candidates=[candidate], gold_events=gold)


def test_malformed_gold_uncertainty_is_invalid_protocol(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    candidate = {"query_id":"q0","window_id":"w0","arm_id":"offline-development-arm","rank":1,"revision_id":"rev-1","start":0,"end":1,"mapping_ref":"map-1","origin":{"numerator":0,"denominator":1},"time_base":{"numerator":1,"denominator":1}}
    gold = [{"query_id":"q0","revision_id":"rev-1","grade":2,"start":0,"end":1,"uncertainty":{"start":-1,"end":0}}]
    with pytest.raises(ValueError, match="uncertainty|protocol"):
        evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64, ranked_candidates=[candidate], gold_events=gold)


def test_missing_family_metric_set_is_invalid_protocol(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    result = evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64)
    incomplete = dict(result.metrics)
    incomplete.pop("family_hit_at_10.semantic.appearance")
    from dataclasses import replace
    assert decide_gate(replace(result, metrics=incomplete), validity="VALID", policy_status="ALLOW", repeat_status="EQUAL") == "INVALID_PROTOCOL"


def _rational(numerator, denominator=1):
    return {"numerator": numerator, "denominator": denominator}


def _final_judgments(tmp_path):
    token_map = ({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path, token_map=token_map, expected_mapping_digest=_mapping_digest_for(token_map))
    return reviewer_judgments(envelope, token_map=token_map)


def _candidate(**overrides):
    row = {"query_id": "q0", "window_id": "w0", "arm_id": "offline-development-arm", "rank": 1, "revision_id": "rev-1",
           "start": _rational(0), "end": _rational(1), "mapping_ref": "map-1",
           "origin": _rational(0), "time_base": _rational(1)}
    row.update(overrides)
    return row


def _gold(**overrides):
    row = {"query_id": "q0", "window_id": "other", "revision_id": "rev-1", "grade": 2,
           "start": _rational(0), "end": _rational(1),
           "uncertainty": {"start": _rational(0), "end": _rational(0)}}
    row.update(overrides)
    return row


def _run_join(tmp_path, candidate, gold):
    judgments = _final_judgments(tmp_path)
    result = evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64,
                      gold_version_digest="g" * 64, query_version_digest="q" * 64,
                      ranked_candidates=[candidate], gold_events=[gold])
    return result.per_query["q0"]["semantic"]


def test_rational_interval_join_matches_on_non_empty_half_open_overlap(tmp_path):
    # Rational wire objects (as build_gold_events emits them) must be consumed
    # exactly, not passed through float(...).
    candidate = _candidate(start=_rational(0), end=_rational(1, 2))
    gold = _gold(start=_rational(1, 3), end=_rational(2, 3))
    assert _run_join(tmp_path, candidate, gold) == 1
    contained = _candidate(start=_rational(1, 4), end=_rational(1, 2))
    assert _run_join(tmp_path, contained, gold) == 1


def test_rational_intervals_that_only_touch_do_not_match(tmp_path):
    # Half-open semantics: [0, 1/2) and [1/2, 3/4) share no point.
    candidate = _candidate(start=_rational(0), end=_rational(1, 2))
    gold = _gold(start=_rational(1, 2), end=_rational(3, 4))
    assert _run_join(tmp_path, candidate, gold) == 0
    # candidate.end == expanded gold start, where the expansion is exact:
    # gold start 1/2 + 1/90000 expanded by u_start 1/90000 -> 1/2.
    expanded = _gold(start=_rational(45001, 90000), end=_rational(3, 4),
                     uncertainty={"start": _rational(1, 90000), "end": _rational(0)})
    assert _run_join(tmp_path, candidate, expanded) == 0


def test_rational_uncertainty_expands_gold_interval_exactly(tmp_path):
    # start-side: gold start 2/3 + 1/90000 expanded by u_start 1/45000 reaches
    # 2/3 - 1/90000, which overlaps candidate [1/3, 2/3). Unexpanded it would
    # not overlap at all.
    candidate = _candidate(start=_rational(1, 3), end=_rational(2, 3))
    gold = _gold(start=_rational(60001, 90000), end=_rational(1),
                 uncertainty={"start": _rational(1, 45000), "end": _rational(0)})
    assert _run_join(tmp_path, candidate, gold) == 1
    # end-side: gold [0, 1/30000) expanded by u_end 1/30000 reaches 1/15000,
    # overlapping candidate [1/20000, 1/10). Unexpanded it would not overlap.
    candidate = _candidate(start=_rational(1, 20000), end=_rational(1, 10))
    gold = _gold(start=_rational(0), end=_rational(1, 30000),
                 uncertainty={"start": _rational(0), "end": _rational(1, 30000)})
    assert _run_join(tmp_path, candidate, gold) == 1


def test_rational_join_is_exact_not_float_rounded(tmp_path):
    # 1/3 approximated at 10^-20 granularity: [n, n+1/10^20) overlaps gold
    # starting at n only under exact rational comparison. Binary float collapses
    # both endpoints onto the same double and would silently report no match.
    numerator = 33333333333333333333
    candidate = _candidate(start=_rational(numerator, 10 ** 20), end=_rational(numerator + 1, 10 ** 20))
    gold = _gold(start=_rational(numerator, 10 ** 20), end=_rational(2, 3))
    assert _run_join(tmp_path, candidate, gold) == 1


def test_numeric_interval_remains_supported_and_must_be_finite(tmp_path):
    # Backward compatibility: plain int and finite float endpoints still work.
    assert _run_join(tmp_path, _candidate(start=0, end=1), _gold(start=0, end=1)) == 1
    assert _run_join(tmp_path, _candidate(start=0.0, end=0.5), _gold(start=0.25, end=0.75)) == 1
    assert _run_join(tmp_path, _candidate(start=0.0, end=0.25), _gold(start=0.25, end=0.75)) == 0
    # Non-finite endpoints are an invalid protocol, never a silent zero.
    with pytest.raises(ValueError, match="protocol"):
        _run_join(tmp_path, _candidate(start=float("nan"), end=1), _gold())
    with pytest.raises(ValueError, match="protocol"):
        _run_join(tmp_path, _candidate(), _gold(start=float("inf"), end=1))


@pytest.mark.parametrize("value", [
    {"numerator": 0, "denominator": 0},
    {"numerator": 1, "denominator": -2},
    {"numerator": True, "denominator": 1},
    {"numerator": "0", "denominator": 1},
    {"numerator": 0},
    "0/1",
    float("inf"),
])
def test_malformed_rational_interval_evidence_is_invalid_protocol(tmp_path, value):
    with pytest.raises(ValueError, match="protocol|mapping|origin|time-base"):
        _run_join(tmp_path, _candidate(start=value), _gold())


@pytest.mark.parametrize("value", [
    {"numerator": 0, "denominator": 0},
    {"numerator": 1, "denominator": -1},
    {"numerator": True, "denominator": 1},
    {"numerator": "1", "denominator": 1},
    -1,
    float("nan"),
])
def test_malformed_rational_gold_uncertainty_is_invalid_protocol(tmp_path, value):
    with pytest.raises(ValueError, match="uncertainty|protocol"):
        _run_join(tmp_path, _candidate(), _gold(uncertainty={"start": value, "end": _rational(0)}))


def test_report_binds_metrics_digest_and_gate_owner(tmp_path):
    envelope = load_reviewer_input(_input(tmp_path), authorized_root=tmp_path,
        token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}), expected_mapping_digest=_mapping_digest_for(({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"})))
    judgments = reviewer_judgments(envelope, token_map=({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"}, {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"}))
    result = evaluate(_rows(), judgments, ranking_digest="r" * 64, baseline_digest="m" * 64, gold_version_digest="g" * 64, query_version_digest="q" * 64)
    projection = report(result, run_id="run-1", authority="owner", reviewers=("reviewer-1", "reviewer-2"), validity="VALID", policy_status="ALLOW", repeat_status="EQUAL", run_manifest={"run_id": "run-1", "gate_owner_id": "owner"})
    assert len(projection.metrics_digest) == 64
    with pytest.raises(ValueError, match="binding"):
        report(result, run_id="run-1", authority="owner", reviewers=(), validity="VALID", policy_status="ALLOW", repeat_status="EQUAL", run_manifest={"run_id": "run-1", "gate_owner_id": "other"})
