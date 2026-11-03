"""Blinding / review-isolation enforcement negatives (Task 5 step 5, D5 context).

Owner requirement: ``blinding.access_scope == "T08_only"`` must be an enforced
access boundary, not a declared literal.  The executable enforcement lives in
``src/gate0/evaluation.py::load_reviewer_input`` (resolved-path containment plus
regular-file requirement) and is wired into the evaluate stage
(``src/gate0/execution.py`` ``_stage_evaluate``), which converts the refusal into
``INVALID_PROTOCOL``.  ``tests/gate0/integration/test_synthetic_end_to_end.py:150``
already covers the end-to-end refusal; this file pins the boundary directly,
including symlink escapes that lexically look inside the authorized root.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from gate0.evaluation import load_reviewer_input

MESSAGE = "review input must be a regular file beneath authorized root"


def _load(path: Path, root: Path):
    return load_reviewer_input(
        path,
        authorized_root=root,
        token_map=[{"blind_arm_token": "ARM_A", "arm_id": "metadata-floor"}],
        expected_mapping_digest="0" * 64,
    )


def test_review_input_beside_the_authorized_root_is_refused(tmp_path: Path) -> None:
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    outside = tmp_path / "reviewer.json"
    outside.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match=MESSAGE):
        _load(outside, authorized)


def test_review_input_symlinked_out_of_the_authorized_root_is_refused(tmp_path: Path) -> None:
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    link = authorized / "reviewer.json"
    link.symlink_to(outside)
    with pytest.raises(ValueError, match=MESSAGE):
        _load(link, authorized)


def test_review_input_directory_is_not_a_regular_file(tmp_path: Path) -> None:
    authorized = tmp_path / "authorized"
    nested = authorized / "reviewer"
    nested.mkdir(parents=True)
    with pytest.raises(ValueError, match=MESSAGE):
        _load(nested, authorized)


def test_authorized_root_itself_is_not_an_acceptable_review_input(tmp_path: Path) -> None:
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    with pytest.raises(ValueError, match=MESSAGE):
        _load(authorized, authorized)


def test_scope_admitted_input_still_must_be_a_valid_reviewer_envelope(tmp_path: Path) -> None:
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    inside = authorized / "reviewer.json"
    inside.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="reviewer input envelope has unknown or missing fields"):
        _load(inside, authorized)
