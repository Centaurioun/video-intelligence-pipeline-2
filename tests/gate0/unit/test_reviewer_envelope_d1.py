"""GT-0 D-1 lane B (P-05) — independent reviewer-envelope assembly tool.

These tests exercise ``gate0.reviewer_envelope`` only.  Every reviewer row is
*artificial test data*: the tool must assemble/validate a blinded two-human
envelope and must never manufacture, infer or "repair" a judgment, a reviewer
identity or a grade.  The compatibility target is the frozen producer
``gate0.evaluation.load_reviewer_input`` (read-only here); the tests roundtrip
through that loader rather than re-implementing its rules.

Negative coverage maps to plan §"Five review-priority negative cases" item 4:
one reviewer, same reviewer twice, token mismatch, extra/missing keys,
duplicate (query, window, token, reviewer), forged digests, grade outside 0–2,
unknown status, adjudication disagreement/unknown adjudication, unknown
query/window and cross-development/evaluation review.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gate0 import reviewer_envelope
from gate0.evaluation import (
    _input_digest_for,
    _mapping_digest_for,
    load_reviewer_input,
    reviewer_judgments,
)
from gate0.reviewer_envelope import (
    ENVELOPE_FIELDS,
    ROW_ALLOWED_FIELDS,
    SCHEMA_VERSION,
    TOKENS,
    build_reviewer_envelope,
    validate_reviewer_envelope,
    write_reviewer_envelope,
)

TOKEN_MAP = (
    {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
    {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
)
REVIEWERS = ("reviewer-1", "reviewer-2")
ARM_IDS = ("metadata-floor", "offline-development-arm")
DIGEST = "d" * 64


def _assertion(query_id: str = "q0") -> dict[str, str]:
    return {"version": "v1", "text": f"synthetic query {query_id}", "digest": DIGEST}


def _row(
    query_id: str = "q0",
    window_id: str = "w0",
    blind_arm_token: str = "arm-a",
    reviewer_id: str = "reviewer-1",
    grade: int = 2,
    **overrides: object,
) -> dict[str, object]:
    row: dict[str, object] = {
        "assertion_id": f"assertion-{query_id}",
        "query_id": query_id,
        "window_id": window_id,
        "blind_arm_token": blind_arm_token,
        "reviewer_id": reviewer_id,
        "grade": grade,
        "ambiguity": "NONE",
        "review_status": "ACCEPTED",
        "assertion": _assertion(query_id),
    }
    row.update(overrides)
    return row


def _group(
    query_id: str = "q0",
    window_id: str = "w0",
    blind_arm_token: str = "arm-a",
    grade: int = 2,
    **overrides: object,
) -> list[dict[str, object]]:
    return [
        _row(query_id, window_id, blind_arm_token, reviewer_id, grade, **overrides)
        for reviewer_id in REVIEWERS
    ]


def _candidate_rows() -> list[dict[str, object]]:
    """Two queries × two arms × two windows × two reviewers: 16 artificial rows."""
    rows: list[dict[str, object]] = []
    for query_id in ("q0", "q1"):
        for token in TOKENS:
            for window_id in ("w0", "w1"):
                rows.extend(
                    _group(query_id=query_id, window_id=window_id, blind_arm_token=token)
                )
    return rows


def _build(rows, **kwargs):
    kwargs.setdefault("token_map", TOKEN_MAP)
    return build_reviewer_envelope(rows, **kwargs)


def _load(envelope, root: Path, **kwargs):
    root.mkdir(parents=True, exist_ok=True)
    path = root / "judgments.json"
    path.write_text(json.dumps(envelope), encoding="utf-8")
    return load_reviewer_input(
        path,
        authorized_root=root,
        token_map=kwargs.pop("token_map", TOKEN_MAP),
        expected_mapping_digest=envelope["blind_mapping_digest"],
        expected_input_digest=envelope["input_digest"],
        **kwargs,
    )


# ---------------------------------------------------------------------------
# B1 — valid synthetic closed envelope, canonical digests, loader roundtrip
# ---------------------------------------------------------------------------


def test_generated_synthetic_two_reviewer_envelope_roundtrips_loader() -> None:
    envelope = _build(_candidate_rows())

    assert set(envelope) == ENVELOPE_FIELDS == {
        "schema_version",
        "input_digest",
        "blind_mapping_digest",
        "rows",
    }
    assert envelope["schema_version"] == SCHEMA_VERSION == "gate0.reviewer-input.v1"
    assert isinstance(envelope["input_digest"], str) and len(envelope["input_digest"]) == 64
    assert isinstance(envelope["blind_mapping_digest"], str)
    assert len(envelope["blind_mapping_digest"]) == 64
    assert all(set(row) <= ROW_ALLOWED_FIELDS for row in envelope["rows"])
    assert len(envelope["rows"]) == 16
    assert {row["blind_arm_token"] for row in envelope["rows"]} == set(TOKENS)
    assert {row["reviewer_id"] for row in envelope["rows"]} == set(REVIEWERS)


def test_canonical_digests_are_stable_under_row_permutation() -> None:
    rows = _candidate_rows()
    forward = _build(rows)
    backward = _build(list(reversed(rows)))

    assert forward == backward
    assert forward["input_digest"] == _input_digest_for(SCHEMA_VERSION, forward["rows"])
    assert forward["blind_mapping_digest"] == _mapping_digest_for(TOKEN_MAP)


def test_rows_are_emitted_in_canonical_order_and_input_is_not_mutated() -> None:
    rows = _candidate_rows()
    snapshot = json.loads(json.dumps(rows))
    envelope = _build(rows)

    keys = [
        (r["query_id"], r["window_id"], r["blind_arm_token"], r["reviewer_id"])
        for r in envelope["rows"]
    ]
    assert keys == sorted(keys)
    assert rows == snapshot, "the assembler must not refashion caller rows in place"


def test_roundtrip_through_frozen_loader_and_judgment_projection(tmp_path: Path) -> None:
    envelope = _build(_candidate_rows())
    root = tmp_path / "authorized"

    loaded = _load(envelope, root)

    assert loaded.schema_version == SCHEMA_VERSION
    assert loaded.input_digest == envelope["input_digest"]
    assert loaded.blind_mapping_digest == envelope["blind_mapping_digest"]
    assert len(loaded.rows) == 16
    judgments = reviewer_judgments(loaded, token_map=TOKEN_MAP)
    assert {j["arm_id"] for j in judgments} == set(ARM_IDS)
    assert len(judgments) == 8


def test_mapping_version_and_config_digest_are_bound_into_the_envelope() -> None:
    rows = _candidate_rows()
    baseline = _build(rows)
    alternate = _build(rows, mapping_version="gate0-v1", config_digest="e" * 64)

    assert baseline["blind_mapping_digest"] != alternate["blind_mapping_digest"]
    assert baseline["input_digest"] == alternate["input_digest"]
    assert alternate["blind_mapping_digest"] == _mapping_digest_for(
        TOKEN_MAP, config_digest="e" * 64
    )


def test_adjudicated_rows_with_shared_reference_are_accepted() -> None:
    rows = _candidate_rows()
    for row in rows:
        if (
            row["query_id"],
            row["window_id"],
            row["blind_arm_token"],
        ) == ("q0", "w0", "arm-a"):
            row["adjudication_ref"] = "adjudication-0"
            row["grade"] = 1

    envelope = _build(rows)

    adjudicated = [row for row in envelope["rows"] if "adjudication_ref" in row]
    assert [(row["grade"], row["adjudication_ref"]) for row in adjudicated] == [
        (1, "adjudication-0"),
        (1, "adjudication-0"),
    ]


def test_declared_reviewer_identities_and_corpus_boundaries_are_enforced_on_success() -> None:
    envelope = _build(
        _candidate_rows(),
        expected_reviewer_ids=REVIEWERS,
        known_query_ids={"q0", "q1"},
        known_window_ids={"w0", "w1"},
        forbidden_query_ids={"dev-0"},
    )
    assert {row["reviewer_id"] for row in envelope["rows"]} == set(REVIEWERS)


def test_build_and_validate_agree_on_a_valid_envelope() -> None:
    envelope = _build(_candidate_rows())
    assert validate_reviewer_envelope(envelope, token_map=TOKEN_MAP) == envelope


def test_build_performs_no_filesystem_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    def _forbid(*args: object, **kwargs: object) -> None:
        raise AssertionError("reviewer-envelope assembly must not read the filesystem")

    monkeypatch.setattr(Path, "read_text", _forbid)
    monkeypatch.setattr(Path, "open", _forbid)
    envelope = _build(_candidate_rows())
    assert len(envelope["rows"]) == 16


def test_module_keeps_the_ranker_and_label_firewall() -> None:
    source = Path(reviewer_envelope.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "gate0.ranking",
        "gate0.labels",
        "gate0.adapters",
        "FakeEmbeddingAdapter",
        "ranked_candidates",
        "gold_events",
    ):
        assert forbidden not in source, forbidden


# ---------------------------------------------------------------------------
# B2 — reviewer identity, blinding and closed-field negatives
# ---------------------------------------------------------------------------


def test_single_reviewer_is_refused() -> None:
    rows = [_row(window_id="w0", blind_arm_token=token) for token in TOKENS]
    with pytest.raises(ValueError, match="exactly two distinct reviewers"):
        _build(rows)


def test_same_reviewer_twice_is_refused() -> None:
    rows = [
        _row(reviewer_id="reviewer-1", window_id="w0", blind_arm_token=token)
        for token in TOKENS
    ]
    rows.append(_row(reviewer_id="reviewer-1", window_id="w0", blind_arm_token="arm-a", grade=0))
    with pytest.raises(ValueError, match="reviewer-1|duplicate|two distinct"):
        _build(rows)


def test_duplicate_judgment_key_is_refused() -> None:
    rows = _group()
    rows.append(_row())
    with pytest.raises(ValueError, match="duplicate reviewer judgment key"):
        _build(rows)


def test_third_reviewer_in_one_judgment_group_is_refused() -> None:
    rows = _group() + [_row(reviewer_id="reviewer-3")]
    with pytest.raises(ValueError, match="exactly two reviewers per judgment"):
        _build(rows)


def test_unknown_blind_arm_token_is_refused() -> None:
    rows = _group() + _group(blind_arm_token="arm-c", window_id="w9")
    with pytest.raises(ValueError, match="unknown blind arm token"):
        _build(rows)


def test_both_arms_must_be_present() -> None:
    rows = _group(window_id="w0") + _group(window_id="w1")
    with pytest.raises(ValueError, match="exactly two blind arm tokens"):
        _build(rows)


@pytest.mark.parametrize("field", ["arm_id", "revision_id", "ranker_id", "score", "provenance"])
def test_extra_reviewer_visible_key_is_refused(field: str) -> None:
    rows = _group()
    rows[0] = dict(rows[0], **{field: "leak"})
    with pytest.raises(ValueError, match="unknown reviewer field"):
        _build(rows)


@pytest.mark.parametrize(
    "field",
    [
        "assertion_id",
        "query_id",
        "window_id",
        "blind_arm_token",
        "reviewer_id",
        "grade",
        "ambiguity",
        "review_status",
        "assertion",
    ],
)
def test_missing_required_reviewer_key_is_refused(field: str) -> None:
    rows = _group()
    rows[0] = {key: value for key, value in rows[0].items() if key != field}
    with pytest.raises(ValueError, match="incomplete reviewer row|unknown reviewer field"):
        _build(rows)


def test_arm_identity_leaking_into_reviewer_visible_text_is_refused() -> None:
    rows = _group()
    rows[0]["assertion"] = {"version": "v1", "text": "metadata-floor result", "digest": DIGEST}
    with pytest.raises(ValueError, match="blinding"):
        _build(rows)


def test_assertion_digest_must_be_a_canonical_sha256_hex_digest() -> None:
    rows = _group()
    rows[0]["assertion"] = {"version": "v1", "text": "synthetic query q0", "digest": "D" * 64}
    with pytest.raises(ValueError, match="assertion digest"):
        _build(rows)


def test_assertion_projection_must_be_exactly_version_text_digest() -> None:
    rows = _group()
    rows[0]["assertion"] = {
        "version": "v1",
        "text": "synthetic query q0",
        "digest": DIGEST,
        "score": 1,
    }
    with pytest.raises(ValueError, match="invalid assertion projection"):
        _build(rows)


# ---------------------------------------------------------------------------
# B2 — grade, status, adjudication negatives
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("grade", [3, -1, "2", 1.5, None, True])
def test_grade_outside_zero_one_two_is_refused(grade: object) -> None:
    rows = _group()
    rows[0]["grade"] = grade
    with pytest.raises(ValueError, match="invalid reviewer grade"):
        _build(rows)


@pytest.mark.parametrize("status", ["FINAL", "rejected", "", None])
def test_unknown_review_status_is_refused(status: object) -> None:
    rows = _group()
    rows[0]["review_status"] = status
    with pytest.raises(ValueError, match="invalid review status"):
        _build(rows)


@pytest.mark.parametrize("status", ["UNREVIEWED", "REJECTED", "AMBIGUOUS"])
def test_non_final_review_is_refused(status: str) -> None:
    rows = _group()
    rows[0]["review_status"] = status
    with pytest.raises(ValueError, match="reviewer judgment is not final"):
        _build(rows)


def test_unknown_ambiguity_is_refused() -> None:
    rows = _group()
    rows[0]["ambiguity"] = "MAYBE"
    with pytest.raises(ValueError, match="invalid reviewer ambiguity"):
        _build(rows)


def test_non_none_ambiguity_is_refused() -> None:
    rows = _group()
    rows[0]["ambiguity"] = "UNCERTAIN"
    with pytest.raises(ValueError, match="reviewer judgment is not final"):
        _build(rows)


def test_grade_disagreement_without_identical_final_grade_is_refused() -> None:
    rows = _group()
    rows[1]["grade"] = 0
    with pytest.raises(ValueError, match="disagreement requires adjudication"):
        _build(rows)


def test_grade_disagreement_with_shared_adjudication_is_still_refused() -> None:
    rows = _group(adjudication_ref="adjudication-0")
    rows[1]["grade"] = 0
    with pytest.raises(ValueError, match="adjudicat"):
        _build(rows)


def test_adjudication_reference_must_be_present_on_both_reviewers() -> None:
    rows = _group()
    rows[0]["adjudication_ref"] = "adjudication-0"
    with pytest.raises(ValueError, match="adjudication_ref"):
        _build(rows)


def test_adjudication_reference_must_match_across_reviewers() -> None:
    rows = _group()
    rows[0]["adjudication_ref"] = "adjudication-0"
    rows[1]["adjudication_ref"] = "adjudication-1"
    with pytest.raises(ValueError, match="adjudication_ref"):
        _build(rows)


@pytest.mark.parametrize("reference", ["", " ", None, 7])
def test_adjudication_reference_must_be_a_non_empty_string(reference: object) -> None:
    rows = _group()
    rows[0]["adjudication_ref"] = reference
    rows[1]["adjudication_ref"] = reference
    with pytest.raises(ValueError, match="adjudication_ref"):
        _build(rows)


# ---------------------------------------------------------------------------
# B2 — caller-declared corpus boundaries (unknown / cross-split review)
# ---------------------------------------------------------------------------


def test_unknown_query_is_refused_when_query_boundary_is_declared() -> None:
    with pytest.raises(ValueError, match="unknown query id"):
        _build(_candidate_rows(), known_query_ids={"q0"})


def test_unknown_window_is_refused_when_window_boundary_is_declared() -> None:
    with pytest.raises(ValueError, match="unknown window id"):
        _build(_candidate_rows(), known_window_ids={"w0"})


def test_crossing_development_and_evaluation_review_is_refused() -> None:
    rows = _group(window_id="w0", blind_arm_token="arm-a") + _group(
        query_id="dev-0", window_id="w0", blind_arm_token="arm-b"
    )
    with pytest.raises(ValueError, match="must not cross development/evaluation"):
        _build(rows, forbidden_query_ids={"dev-0"})


def test_expected_reviewer_identity_mismatch_is_refused() -> None:
    with pytest.raises(ValueError, match="reviewer identit"):
        _build(_candidate_rows(), expected_reviewer_ids=("reviewer-1", "reviewer-9"))


# ---------------------------------------------------------------------------
# B2 — forged digests / malformed envelope input
# ---------------------------------------------------------------------------


def test_forged_input_digest_is_refused() -> None:
    envelope = _build(_candidate_rows())
    envelope["input_digest"] = "0" * 64
    with pytest.raises(ValueError, match="wrong reviewer input digest"):
        validate_reviewer_envelope(envelope, token_map=TOKEN_MAP)


def test_forged_blind_mapping_digest_is_refused() -> None:
    envelope = _build(_candidate_rows())
    envelope["blind_mapping_digest"] = "0" * 64
    with pytest.raises(ValueError, match="wrong blinding mapping digest"):
        validate_reviewer_envelope(envelope, token_map=TOKEN_MAP)


def test_expected_digest_pin_mismatch_is_refused() -> None:
    envelope = _build(_candidate_rows())
    with pytest.raises(ValueError, match="wrong reviewer input digest"):
        validate_reviewer_envelope(
            envelope, token_map=TOKEN_MAP, expected_input_digest="1" * 64
        )


def test_unknown_envelope_field_is_refused() -> None:
    envelope = _build(_candidate_rows())
    envelope["human_reviewed"] = True
    with pytest.raises(ValueError, match="unknown or missing fields"):
        validate_reviewer_envelope(envelope, token_map=TOKEN_MAP)


def test_row_order_in_a_supplied_envelope_is_revalidated_canonically() -> None:
    envelope = _build(_candidate_rows())
    shuffled = dict(envelope, rows=list(reversed(envelope["rows"])))
    with pytest.raises(ValueError, match="wrong reviewer input digest"):
        validate_reviewer_envelope(shuffled, token_map=TOKEN_MAP)


# ---------------------------------------------------------------------------
# B2 — token map / blinding-config negatives
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "token_map",
    [
        ({"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},),
        (
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
            {"blind_arm_token": "arm-b", "arm_id": "metadata-floor"},
        ),
        (
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
            {"blind_arm_token": "arm-c", "arm_id": "offline-development-arm"},
        ),
        (
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor", "note": "x"},
            {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
        ),
        (
            {"blind_arm_token": "arm-a", "arm_id": ""},
            {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
        ),
        (
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
            {"blind_arm_token": "arm-b", "arm_id": "metadata-floor"},
        ),
    ],
)
def test_invalid_token_map_is_refused(token_map) -> None:
    with pytest.raises(ValueError):
        build_reviewer_envelope(_candidate_rows(), token_map=token_map)


def test_arm_ids_may_not_equal_blind_tokens() -> None:
    token_map = (
        {"blind_arm_token": "arm-a", "arm_id": "arm-b"},
        {"blind_arm_token": "arm-b", "arm_id": "metadata-floor"},
    )
    with pytest.raises(ValueError, match="token_map|arm_id"):
        build_reviewer_envelope(_candidate_rows(), token_map=token_map)


def test_invalid_mapping_version_or_config_digest_is_refused() -> None:
    with pytest.raises(ValueError, match="mapping_version"):
        _build(_candidate_rows(), mapping_version="")
    with pytest.raises(ValueError, match="config_digest"):
        _build(_candidate_rows(), config_digest="not-a-digest")


@pytest.mark.parametrize("rows", [(), [], [("not-a-mapping",)], ["row"], [{}, {}]])
def test_malformed_rows_are_refused(rows) -> None:
    with pytest.raises(ValueError):
        _build(rows)


# ---------------------------------------------------------------------------
# B2 — atomic emission, guarded by the caller-provided root
# ---------------------------------------------------------------------------


def _write(rows, root: Path, name: str = "judgments.json"):
    envelope = _build(rows)
    path = write_reviewer_envelope(envelope, root / name, authorized_root=root, token_map=TOKEN_MAP)
    return envelope, path


def test_atomic_write_roundtrips_through_the_loader(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    root.mkdir()
    envelope, path = _write(_candidate_rows(), root)

    assert path == (root / "judgments.json").resolve()
    assert json.loads(path.read_text(encoding="utf-8")) == envelope
    loaded = load_reviewer_input(
        path,
        authorized_root=root,
        token_map=TOKEN_MAP,
        expected_mapping_digest=envelope["blind_mapping_digest"],
        expected_input_digest=envelope["input_digest"],
    )
    assert len(loaded.rows) == 16
    assert not list(root.glob("*.tmp"))


def test_write_outside_the_authorized_root_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    root.mkdir()
    envelope = _build(_candidate_rows())
    with pytest.raises(ValueError, match="beneath authorized root"):
        write_reviewer_envelope(
            envelope, tmp_path / "escape.json", authorized_root=root, token_map=TOKEN_MAP
        )
    assert not (tmp_path / "escape.json").exists()


def test_write_to_the_authorized_root_itself_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    root.mkdir()
    with pytest.raises(ValueError, match="beneath authorized root"):
        write_reviewer_envelope(
            _build(_candidate_rows()), root, authorized_root=root, token_map=TOKEN_MAP
        )


def test_write_refuses_a_directory_target(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    (root / "judgments.json").mkdir(parents=True)
    with pytest.raises(ValueError, match="regular file"):
        _write(_candidate_rows(), root)


def test_write_refuses_an_invalid_envelope_before_touching_the_filesystem(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    root.mkdir()
    envelope = _build(_candidate_rows())
    envelope["input_digest"] = "0" * 64
    with pytest.raises(ValueError, match="wrong reviewer input digest"):
        write_reviewer_envelope(
            envelope, root / "judgments.json", authorized_root=root, token_map=TOKEN_MAP
        )
    assert list(root.iterdir()) == []


def test_failed_assembly_never_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "authorized"
    output.mkdir()
    with pytest.raises(ValueError):
        _build(_group() + [_row(reviewer_id="reviewer-9")])
    assert list(output.iterdir()) == []


def test_invalid_envelope_write_preserves_the_existing_target(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    root.mkdir()
    envelope = _build(_candidate_rows())
    target = root / "judgments.json"
    target.write_text("previous", encoding="utf-8")
    envelope["blind_mapping_digest"] = "0" * 64
    with pytest.raises(ValueError):
        write_reviewer_envelope(envelope, target, authorized_root=root, token_map=TOKEN_MAP)
    assert target.read_text(encoding="utf-8") == "previous"
    assert [p.name for p in root.iterdir()] == ["judgments.json"]


# ---------------------------------------------------------------------------
# B2 — "no fabricated human judgment" provenance negatives
# ---------------------------------------------------------------------------


def test_module_exposes_no_authenticity_claim_and_requires_caller_supplied_rows() -> None:
    envelope = _build(_candidate_rows())
    assert set(envelope) == ENVELOPE_FIELDS
    assert not any("synthetic" in key or "authentic" in key for key in envelope)
    assert "human" in (reviewer_envelope.__doc__ or "").lower()


# ---------------------------------------------------------------------------
# B2 — reviewer-flagged hardening: caller-declared hidden identities,
# writer boundary forwarding, and durable PENDING documentation
# ---------------------------------------------------------------------------


def test_declared_hidden_identity_in_free_text_is_refused() -> None:
    rows = _candidate_rows()
    rows[0]["assertion"]["text"] = "synthetic query q0 rev-abc123"

    # Undeclared free-text identity leakage is a documented PENDING residual:
    # the assembler cannot know every revision/ranker spelling by itself.
    _build(rows)

    with pytest.raises(ValueError, match="hidden identity"):
        _build(rows, forbidden_identifiers=("rev-abc123",))


def test_writer_forwards_caller_declared_boundaries(tmp_path: Path) -> None:
    root = tmp_path / "authorized"
    root.mkdir()
    envelope = _build(_candidate_rows())
    with pytest.raises(ValueError, match="unknown query id"):
        write_reviewer_envelope(
            envelope,
            root / "judgments.json",
            authorized_root=root,
            token_map=TOKEN_MAP,
            known_query_ids={"q0"},
        )
    assert not (root / "judgments.json").exists()
    assert list(root.iterdir()) == []


def test_docstring_records_loader_undetectable_pending_issues() -> None:
    doc = (reviewer_envelope.__doc__ or "").lower()
    for marker in (
        "pending",
        "corpus correspondence",
        "adjudication-ref granularity",
        "adjudication provenance",
        "revision/ranker identity",
        "cross-row assertion consistency",
    ):
        assert marker in doc, marker
