"""GT-0 D-2 / PKT-D2-2 — reviewer-envelope config-digest and identity binding.

The Gate-0 reviewer envelope is binding evidence: it must belong to *one*
frozen run configuration and to the *declared two-person reviewer set*.  The
pre-fix executable pipeline violated that contract in two places:

* ``src/gate0/execution.py`` computed the blinding-mapping digest with the
  placeholder ``config_digest`` ``"0" * 64`` in both ``prepare`` and
  ``evaluate``, while the reviewer loader independently defaulted to the same
  placeholder.  A real config-bound envelope was therefore refused and a
  placeholder-bound envelope was accepted under a run whose real canonical
  config digest is non-zero.
* ``src/gate0/evaluation.py`` never bound the envelope's reviewer identities to
  the configured ``policy.reviewer_ids`` set, so two arbitrary reviewer ids
  could satisfy the two-reviewer shape.

These tests are synthetic, local-only and use the frozen default configuration
(``config/gate0/default.json``).  They never use real media, a model, a provider
call or a real human review.  D-2 genuine reviewer authenticity remains
``NOT_OBSERVED``; D-3 execution authorization is unchanged.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from gate0.config_freeze import canonical_config_digest
from gate0.evaluation import (
    _input_digest_for,
    _mapping_digest_for,
    load_reviewer_input,
)
from gate0.execution import _mapping_digest as _execution_mapping_digest
from gate0.execution import _stage_evaluate

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = REPO_ROOT / "config/gate0/default.json"
FIXTURE_ROOT = REPO_ROOT / "tests/gate0/fixtures/synthetic-input"

if str(FIXTURE_ROOT) not in sys.path:
    sys.path.insert(0, str(FIXTURE_ROOT))

import generate  # noqa: E402  (frozen synthetic-input generator, reused verbatim)

ZERO_DIGEST = "0" * 64
REVIEWERS = ("reviewer-1", "reviewer-2")


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------


def _config(tmp_path: Path) -> tuple[dict, Path]:
    """Load the frozen config and relocate only the authorized review root."""
    config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    authorized = tmp_path / "authorized"
    authorized.mkdir()
    config["policy"]["review_input"]["authorized_root"] = str(authorized)
    return config, authorized


def _token_map(config: dict) -> list[dict]:
    return [dict(row) for row in config["blinding"]["token_map"]]


def _mapping_version(config: dict) -> str:
    return str(config["blinding"]["mapping_version"])


def _row(query_id: str, window_id: str, token: str, reviewer_id: str) -> dict:
    return {
        "assertion_id": f"assertion-{query_id}-{token}",
        "query_id": query_id,
        "window_id": window_id,
        "blind_arm_token": token,
        "reviewer_id": reviewer_id,
        "grade": 2,
        "ambiguity": "NONE",
        "review_status": "ACCEPTED",
        "assertion": {"version": "v1", "text": f"synthetic query {query_id}", "digest": "d" * 64},
    }


def _rows(*, reviewers: tuple[str, ...] = REVIEWERS, queries: int = 24) -> list[dict]:
    tokens = tuple(str(row["blind_arm_token"]) for row in _token_map(json.loads(DEFAULT_CONFIG.read_text())))
    rows = []
    for index in range(queries):
        for token in tokens:
            for reviewer in reviewers:
                rows.append(_row(f"q{index}", f"w{index}", token, reviewer))
    return rows


def _write_envelope(path: Path, rows: list[dict], config: dict, *, config_digest: str) -> Path:
    token_map = _token_map(config)
    envelope = {
        "schema_version": "gate0.reviewer-input.v1",
        "input_digest": _input_digest_for("gate0.reviewer-input.v1", rows),
        "blind_mapping_digest": _mapping_digest_for(
            token_map, mapping_version=_mapping_version(config), config_digest=config_digest
        ),
        "rows": rows,
    }
    path.write_text(json.dumps(envelope), encoding="utf-8")
    return path


def _manifest(config: dict, *, config_digest: str | None = None) -> dict:
    return {
        "run_id": "run_d2_binding",
        "config_digest": canonical_config_digest(config) if config_digest is None else config_digest,
        "ranking_digest": "1" * 64,
        "baseline_digest": "2" * 64,
        "gold_version_digest": "3" * 64,
        "query_version_digest": "4" * 64,
        "windows": [],
    }


def _run_evaluate(tmp_path: Path, config: dict, envelope: Path, manifest: dict | None = None):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    for name in ("queries.jsonl", "gold_events.jsonl", "ranked_candidates.jsonl"):
        (run_dir / name).write_text("", encoding="utf-8")
    return _stage_evaluate(
        run_dir,
        _manifest(config) if manifest is None else manifest,
        config,
        tmp_path / "config.json",
        envelope,
    )


# ---------------------------------------------------------------------------
# (a) a real config-bound mapping must be accepted, not refused
# ---------------------------------------------------------------------------


def test_real_config_bound_envelope_reaches_evaluation_not_mapping_refusal(tmp_path: Path) -> None:
    """Defect (a): the envelope bound to the real run digest must pass binding.

    The minimal run directory carries no query rows, so ``evaluate`` refuses
    afterwards with an ``EVALUATION:`` reason.  Reaching that failure proves the
    config-bound envelope was *not* refused by the blinding-mapping binding.
    """
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)

    code, projection = _run_evaluate(tmp_path, config, envelope)

    assert code == 30
    reason = str(projection["reason"])
    assert "wrong blinding mapping digest" not in reason, reason
    assert "reviewer identities do not match" not in reason, reason
    assert reason.startswith("EVALUATION:"), reason


# ---------------------------------------------------------------------------
# (b) a placeholder zero-digest mapping must not pass under a real config
# ---------------------------------------------------------------------------


def test_placeholder_zero_digest_envelope_is_refused_under_real_run_config(tmp_path: Path) -> None:
    """Defect (b): a zero-digest envelope previously validated under a real run."""
    config, authorized = _config(tmp_path)
    assert canonical_config_digest(config) != ZERO_DIGEST
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=ZERO_DIGEST)

    code, projection = _run_evaluate(tmp_path, config, envelope)

    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "REVIEW_INPUT:wrong blinding mapping digest"


def test_zero_digest_is_not_the_canonical_run_config_digest(tmp_path: Path) -> None:
    config, _ = _config(tmp_path)
    digest = canonical_config_digest(config)
    assert isinstance(digest, str) and len(digest) == 64
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    assert _mapping_digest_for(token_map, mapping_version=mapping_version, config_digest=digest) != (
        _mapping_digest_for(token_map, mapping_version=mapping_version, config_digest=ZERO_DIGEST)
    )


# ---------------------------------------------------------------------------
# (c) reviewer identities must match the declared two-person set
# ---------------------------------------------------------------------------


def test_evaluate_refuses_reviewer_outside_declared_two_person_set(tmp_path: Path) -> None:
    """Defect (c): two arbitrary reviewer ids used to satisfy the shape check."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    rows = _rows(reviewers=("reviewer-1", "reviewer-3"))
    envelope = _write_envelope(authorized / "review.json", rows, config, config_digest=digest)

    code, projection = _run_evaluate(tmp_path, config, envelope)

    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert "reviewer identities do not match the declared reviewer set" in str(projection["reason"])


def test_loader_binds_envelope_identities_to_declared_set(tmp_path: Path) -> None:
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    rows = _rows(reviewers=("reviewer-1", "reviewer-3"))
    envelope = _write_envelope(authorized / "review.json", rows, config, config_digest=digest)

    with pytest.raises(ValueError, match="reviewer identities do not match the declared reviewer set"):
        load_reviewer_input(
            envelope,
            authorized_root=authorized,
            token_map=token_map,
            expected_mapping_digest=_mapping_digest_for(
                token_map, mapping_version=mapping_version, config_digest=digest
            ),
            expected_reviewer_ids=REVIEWERS,
            mapping_version=mapping_version,
            config_digest=digest,
        )


def test_loader_accepts_the_declared_two_person_set(tmp_path: Path) -> None:
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)

    loaded = load_reviewer_input(
        envelope,
        authorized_root=authorized,
        token_map=token_map,
        expected_mapping_digest=_mapping_digest_for(
            token_map, mapping_version=mapping_version, config_digest=digest
        ),
        expected_reviewer_ids=list(config["policy"]["reviewer_ids"]),
        mapping_version=mapping_version,
        config_digest=digest,
    )

    assert {row.reviewer_id for row in loaded.rows} == set(REVIEWERS)


# ---------------------------------------------------------------------------
# canonical algorithm preservation and manifest/config cross-check
# ---------------------------------------------------------------------------


def test_mapping_digest_algorithm_is_preserved_across_execution_and_loader(tmp_path: Path) -> None:
    """Both canonical mapping-digest helpers must stay byte-identical."""
    config, _ = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    assert _execution_mapping_digest(
        token_map, mapping_version=mapping_version, config_digest=digest
    ) == _mapping_digest_for(token_map, mapping_version=mapping_version, config_digest=digest)
    # The legacy zero placeholder remains a *documented* non-canonical value.
    assert _execution_mapping_digest(
        token_map, mapping_version=mapping_version, config_digest=ZERO_DIGEST
    ) == _mapping_digest_for(token_map, mapping_version=mapping_version, config_digest=ZERO_DIGEST)


def test_stage_refuses_manifest_digest_that_does_not_match_loaded_config(tmp_path: Path) -> None:
    """Manifest evidence is not authority on its own; the loaded config must agree."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)
    tampered = _manifest(config, config_digest=ZERO_DIGEST)

    code, projection = _run_evaluate(tmp_path, config, envelope, manifest=tampered)

    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "CONFIG_DIGEST_MISMATCH"


# ---------------------------------------------------------------------------
# compatibility disposition: existing synthetic zero-digest callers
# ---------------------------------------------------------------------------


def test_legacy_synthetic_fixture_default_digest_cannot_satisfy_the_binding(tmp_path: Path) -> None:
    """The checked-in generator's legacy zero default is compatibility-only.

    ``tests/gate0/fixtures/synthetic-input/generate.py::write_review_input``
    keeps its historical ``config_digest="0" * 64`` default so that recorded
    historical reproduction scripts stay reproducible.  Active regression call
    sites now pass the run's manifest ``config_digest`` explicitly; an envelope
    produced with the zero default must be refused by the bound loader.
    """
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    labels = {"queries": [{"query_id": "q0", "split": "EVALUATION", "text": "synthetic", "presence": "POSITIVE"}],
              "grade2_targets": []}
    windows = [{"window_id": "w0", "revision_id": "rev", "window_index": 0}]
    # No config_digest argument: this is exactly the old zero-digest behaviour.
    envelope = generate.write_review_input(
        authorized / "review.json", labels, windows, token_map, mapping_version=mapping_version
    )
    payload = json.loads(envelope.read_text(encoding="utf-8"))
    assert payload["blind_mapping_digest"] == _mapping_digest_for(
        token_map, mapping_version=mapping_version, config_digest=ZERO_DIGEST
    )
    with pytest.raises(ValueError, match="wrong blinding mapping digest"):
        load_reviewer_input(
            envelope,
            authorized_root=authorized,
            token_map=token_map,
            expected_mapping_digest=_mapping_digest_for(
                token_map, mapping_version=mapping_version, config_digest=digest
            ),
            mapping_version=mapping_version,
            config_digest=digest,
        )


def test_loader_default_digest_remains_backward_compatible_for_legacy_callers(tmp_path: Path) -> None:
    """Existing direct loader callers that pass the zero digest keep working.

    Backward compatibility is deliberate: the P-05 envelope suite exercises the
    loader with synthetic zero-bound envelopes.  The executable pipeline no
    longer uses this default; it always supplies the run's real digest.
    """
    config, authorized = _config(tmp_path)
    rows = _rows()
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    envelope = _write_envelope(authorized / "review.json", rows, config, config_digest=ZERO_DIGEST)

    loaded = load_reviewer_input(
        envelope,
        authorized_root=authorized,
        token_map=token_map,
        expected_mapping_digest=_mapping_digest_for(
            token_map, mapping_version=mapping_version, config_digest=ZERO_DIGEST
        ),
    )

    assert {row.reviewer_id for row in loaded.rows} == set(REVIEWERS)


# ---------------------------------------------------------------------------
# cycle-3 adversarial refinements: fail-closed manifest and identity inputs
# ---------------------------------------------------------------------------


def test_manifest_missing_config_digest_fails_closed(tmp_path: Path) -> None:
    """Absent manifest digest evidence is refused, never treated as the placeholder."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)
    manifest = _manifest(config)
    manifest.pop("config_digest")

    code, projection = _run_evaluate(tmp_path, config, envelope, manifest=manifest)

    assert code == 30
    assert projection["status"] == "INVALID_PROTOCOL"
    assert projection["reason"] == "CONFIG_DIGEST_MISMATCH"


def test_envelope_bound_to_a_different_configuration_is_refused(tmp_path: Path) -> None:
    """A digest that binds some *other* configuration cannot satisfy this run."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    other = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    other["policy"]["review_input"]["authorized_root"] = str(tmp_path / "other-root")
    other_digest = canonical_config_digest(other)
    assert other_digest != digest
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=other_digest)

    code, projection = _run_evaluate(tmp_path, config, envelope)

    assert code == 30
    assert projection["reason"] == "REVIEW_INPUT:wrong blinding mapping digest"


@pytest.mark.parametrize("declared", ["reviewer-1", b"reviewer-1"])
def test_loader_rejects_non_iterable_expected_reviewer_ids(tmp_path: Path, declared) -> None:
    """A bare string/bytes is not a reviewer-identity set."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)

    with pytest.raises(ValueError, match="expected_reviewer_ids must be an iterable of identifiers"):
        load_reviewer_input(
            envelope,
            authorized_root=authorized,
            token_map=token_map,
            expected_mapping_digest=_mapping_digest_for(
                token_map, mapping_version=mapping_version, config_digest=digest
            ),
            expected_reviewer_ids=declared,
            mapping_version=mapping_version,
            config_digest=digest,
        )


def test_loader_rejects_non_string_expected_reviewer_ids(tmp_path: Path) -> None:
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)

    with pytest.raises(ValueError, match="expected_reviewer_ids must contain only strings"):
        load_reviewer_input(
            envelope,
            authorized_root=authorized,
            token_map=token_map,
            expected_mapping_digest=_mapping_digest_for(
                token_map, mapping_version=mapping_version, config_digest=digest
            ),
            expected_reviewer_ids=(1, 2),
            mapping_version=mapping_version,
            config_digest=digest,
        )


def test_loader_identity_binding_is_order_insensitive(tmp_path: Path) -> None:
    """The configured set, not its declared order, is the identity authority."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)

    loaded = load_reviewer_input(
        envelope,
        authorized_root=authorized,
        token_map=token_map,
        expected_mapping_digest=_mapping_digest_for(
            token_map, mapping_version=mapping_version, config_digest=digest
        ),
        expected_reviewer_ids=("reviewer-2", "reviewer-1"),
        mapping_version=mapping_version,
        config_digest=digest,
    )

    assert {row.reviewer_id for row in loaded.rows} == set(REVIEWERS)

def test_loader_rejects_unhashable_expected_reviewer_id_element(tmp_path: Path) -> None:
    """Non-string identity elements are refused with ValueError, not TypeError."""
    config, authorized = _config(tmp_path)
    digest = canonical_config_digest(config)
    token_map = _token_map(config)
    mapping_version = _mapping_version(config)
    envelope = _write_envelope(authorized / "review.json", _rows(), config, config_digest=digest)

    with pytest.raises(ValueError, match="expected_reviewer_ids must contain only strings"):
        load_reviewer_input(
            envelope,
            authorized_root=authorized,
            token_map=token_map,
            expected_mapping_digest=_mapping_digest_for(
                token_map, mapping_version=mapping_version, config_digest=digest
            ),
            expected_reviewer_ids=(['reviewer-1'], 'reviewer-2'),
            mapping_version=mapping_version,
            config_digest=digest,
        )
