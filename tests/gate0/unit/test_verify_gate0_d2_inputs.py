"""PKT-D2-1: deterministic, text-only D-2 Owner-input intake validator.

Chronological RED evidence (recorded in the PR body): this module is exercised
before ``gate0.d2_intake`` exists, so collection fails with
``ModuleNotFoundError: No module named 'gate0.d2_intake'``.

Contract under test (``docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md``
Part C): the thirty stable field IDs are classified deterministically into
VERIFIED / PENDING / BLOCKED / NOT_OBSERVED; BLOCKED outranks PENDING;
observation-only rows are NOT_OBSERVED; a placeholder, media path, duplicate /
missing / unknown field ID, or any authorization claim refuses the whole package
with exit 2; no output row can ever be AUTHORIZED / GRANTED / FROZEN / PASS; a
synthetic fixture can never yield VERIFIED real-Owner evidence; identical input
must produce byte-identical output; and the validator must never stat, open,
list, hash or decode a declared corpus/media path.

Every fixture here is artificial metadata.  No real media, model, corpus or
network is touched.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import sys
from pathlib import Path

import pytest
from gate0 import d2_intake
from gate0.canonical_json import canonical_bytes

REPO_ROOT = Path(__file__).resolve().parents[3]

FAMILIES = (
    "APPEARANCE",
    "VISIBLE_ACTION",
    "INTERACTION",
    "SCENE_COMPOSITION_CAMERA_MOVEMENT",
)
ZERO_DIGEST = "0" * 64

BASELINE = {
    "G0-D2-01": "PENDING",
    "G0-D2-02": "BLOCKED",
    "G0-D2-03": "BLOCKED",
    "G0-D2-04": "BLOCKED",
    "G0-D2-05": "BLOCKED",
    "G0-D2-06": "BLOCKED",
    "G0-D2-07": "BLOCKED",
    "G0-D2-08": "BLOCKED",
    "G0-D2-09": "BLOCKED",
    "G0-D2-10": "PENDING",
    "G0-D2-11": "PENDING",
    "G0-D2-12": "PENDING",
    "G0-D2-13": "BLOCKED",
    "G0-D2-14": "PENDING",
    "G0-D2-15": "BLOCKED",
    "G0-D2-16": "BLOCKED",
    "G0-D2-17": "PENDING",
    "G0-D2-18": "NOT_OBSERVED",
    "G0-D2-19": "NOT_OBSERVED",
    "G0-D2-20": "BLOCKED",
    "G0-D2-21": "BLOCKED",
    "G0-D2-22": "BLOCKED",
    "G0-D2-23": "BLOCKED",
    "G0-D2-24": "BLOCKED",
    "G0-D2-25": "BLOCKED",
    "G0-D2-26": "PENDING",
    "G0-D2-27": "BLOCKED",
    "G0-D2-28": "BLOCKED",
    "G0-D2-29": "BLOCKED",
    "G0-D2-30": "BLOCKED",
}
BASELINE_COUNTS = {"VERIFIED": 0, "PENDING": 7, "BLOCKED": 21, "NOT_OBSERVED": 2}


# ---------------------------------------------------------------------------
# synthetic package builders (artifact generation only; no media)
# ---------------------------------------------------------------------------

def _digest_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def _artifact_digest(document) -> str:
    return _digest_bytes(canonical_bytes(document))


def _editor_queries(presence_counts=None, per_family=6, dev_count=8):
    presence_counts = presence_counts or {}
    queries = []
    for family in FAMILIES:
        for index in range(per_family):
            queries.append({
                "query_id": f"q_eval_{family.lower()}_{index}",
                "text": f"editor query {family} {index}",
                "family": family,
                "presence": "POSITIVE",
                "split": "EVALUATION",
            })
    for index in range(presence_counts.get("ABSENT", 8)):
        queries.append({
            "query_id": f"q_eval_absent_{index}",
            "text": f"editor absent query {index}",
            "family": FAMILIES[index % 4],
            "presence": "ABSENT",
            "split": "EVALUATION",
        })
    for index in range(presence_counts.get("DEVELOPMENT", dev_count)):
        queries.append({
            "query_id": f"q_dev_{index}",
            "text": f"editor development query {index}",
            "family": FAMILIES[index % 4],
            "presence": "POSITIVE",
            "split": "DEVELOPMENT",
        })
    return {"schema_version": "gate0.editor-queries.v1", "query_version": "editor-v1",
            "queries": queries}


def _corpus_designation(*, sessions=4, revisions=6, total_minutes=90):
    request = {"schema_version": "gate0.d2-corpus-designation.v1"}
    request["sessions"] = [
        {"session_id": f"sess_{index}", "duration_minutes": max(1, total_minutes // sessions)}
        for index in range(sessions)
    ]
    rows = []
    for index in range(revisions):
        split = "DEVELOPMENT" if index == revisions - 1 else "EVALUATION"
        rows.append({
            "revision_id": f"rev_{index}",
            "session_id": f"sess_{index % sessions}",
            "duration_minutes": total_minutes // revisions,
            "split": split,
            "families": [FAMILIES[index % 4]],
        })
    request["revisions"] = rows
    request["family_coverage"] = list(FAMILIES)
    return request


def _reviewers(reviewer_ids=("reviewer_a", "reviewer_b")):
    return {"schema_version": "gate0.d2-reviewers.v1",
            "reviewer_ids": list(reviewer_ids),
            "appointment_authority": "gate0-owner appointment decision (text-only)"}


def _blinding(token_map=None):
    return {
        "schema_version": "gate0.d2-blinding.v1",
        "token_map": token_map or [
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
            {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
        ],
        "reviewer_visible_fields": ["blind_arm_token"],
        "reviewer_hidden_fields": ["arm_id"],
    }


def _owner_binding(owner_id="owner_alpha"):
    return {"schema_version": "gate0.d2-owner-binding.v1",
            "config_gate_owner_id": owner_id,
            "manifest_gate_owner_id": owner_id}


ARTIFACTS = {
    "corpus-designation.json": _corpus_designation,
    "editor-queries.json": _editor_queries,
    "reviewers.json": _reviewers,
    "blinding.json": _blinding,
    "owner-binding.json": _owner_binding,
}


def _record(*artifacts):
    return {"declared_status": "COMPLETE",
            "evidence": [{"artifact": name, "digest": "<computed>"} for name in artifacts]}


def _write_package(tmp_path: Path, *, records=None, artifacts=None, fixture=True,
                   attester_kind=None, package_id="d2p_fixture_package", extra=None):
    """Write an artificial D-2 package and return its directory."""
    package_dir = tmp_path / "d2-package"
    package_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {name: (document() if callable(document) else document)
                 for name, document in {**ARTIFACTS, **(artifacts or {})}.items()}
    if attester_kind is None:
        attester_kind = "SYNTHETIC_FIXTURE" if fixture else "OWNER_SIGNED"

    fields = {}
    for field_id in BASELINE:
        if records and field_id in records:
            record = dict(records[field_id])
            evidence = []
            for entry in record.get("evidence", []):
                name = entry["artifact"]
                if entry["digest"] == "<computed>":
                    document = artifacts[name]
                    digest = _artifact_digest(document)
                else:
                    digest = entry["digest"]
                evidence.append({"artifact": name, "digest": digest})
            record["evidence"] = evidence
            fields[field_id] = record
        else:
            fields[field_id] = {"declared_status": "ABSENT"}

    for name, document in artifacts.items():
        path = package_dir / name
        path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    package = {
        "schema_version": d2_intake.D2_PACKAGE_SCHEMA_VERSION,
        "package_id": package_id,
        "fixture": fixture,
        "attestation": {"attester_id": "gate0-owner", "attester_kind": attester_kind},
        "fields": fields,
    }
    if extra:
        package.update(extra)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    manifest.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")
    return package_dir


def _complete_records():
    """Declare all seven text-closable rows complete with real (synthetic) artifacts."""
    return {
        "G0-D2-01": _record("corpus-designation.json"),
        "G0-D2-10": _record("editor-queries.json"),
        "G0-D2-11": _record("editor-queries.json"),
        "G0-D2-12": _record("editor-queries.json"),
        "G0-D2-14": _record("reviewers.json"),
        "G0-D2-17": _record("blinding.json"),
        "G0-D2-26": _record("owner-binding.json"),
    }


def _install_package_only_guard(monkeypatch, package_dir: Path) -> None:
    """Fail if the validator touches anything outside the D-2 package directory.

    This guard is lexical (``abspath``): it cannot follow a symlink, because
    ``realpath`` itself calls the ``os.stat``/``os.lstat`` hooks patched here.
    Symlink escape is instead refused by the module and asserted by
    ``test_symlink_artifact_escaping_package_is_refused``.
    """
    root = os.path.abspath(str(package_dir))

    def guard(real, label):
        def wrapped(path, *args, **kwargs):
            target = os.path.abspath(str(path))
            inside = target == root or target.startswith(root + os.sep)
            # Resolving an absolute package path legitimately stats its ancestor
            # directories; ancestors are allowed, siblings and the declared root
            # are not.
            ancestor = root.startswith(target + os.sep)
            if not inside and not ancestor:
                raise AssertionError(f"validator touched path outside package: {label}: {path}")
            return real(path, *args, **kwargs)
        return wrapped

    for module, name in ((os, "stat"), (os, "lstat"), (os, "open"), (os, "listdir"),
                         (os, "scandir"), (io, "open")):
        monkeypatch.setattr(module, name, guard(getattr(module, name), name))


def _load_cli():
    path = REPO_ROOT / "scripts" / "verify_gate0_d2_inputs.py"
    spec = importlib.util.spec_from_file_location("verify_gate0_d2_inputs", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# registry contract
# ---------------------------------------------------------------------------

def test_thirty_stable_field_ids_in_matrix_order():
    assert d2_intake.D2_FIELD_IDS == tuple(BASELINE)
    assert len(d2_intake.D2_FIELDS) == 30
    assert [field.ordinal for field in d2_intake.D2_FIELDS] == list(range(1, 31))


def test_state_vocabulary_is_exactly_the_four_contract_states():
    assert d2_intake.STATES == ("VERIFIED", "PENDING", "BLOCKED", "NOT_OBSERVED")
    assert set(d2_intake.D2_BASELINE_STATES.values()) <= set(d2_intake.STATES)
    assert "VERIFIED" not in set(d2_intake.D2_BASELINE_STATES.values())


def test_every_field_retains_authority_evidence_and_ruling():
    for field in d2_intake.D2_FIELDS:
        assert field.controlling_authority
        assert field.expected_evidence
        assert field.domain.startswith("B.")
        if field.state_rule == d2_intake.RULE_RULING:
            assert field.unresolved_ruling, field.field_id
        if field.state_rule == d2_intake.RULE_OBSERVATION:
            assert field.observation_only is True
        assert field.title


def test_no_registry_state_uses_authorization_vocabulary():
    forbidden = {"AUTHORIZED", "GRANTED", "FROZEN", "PASS"}
    for field in d2_intake.D2_FIELDS:
        assert field.state_rule.upper() not in forbidden
    assert set(d2_intake.D2_BASELINE_STATES.values()).isdisjoint(forbidden)


# ---------------------------------------------------------------------------
# baseline equivalence (checklist Part B) on an empty package
# ---------------------------------------------------------------------------

def test_empty_package_reproduces_checklist_baseline(tmp_path):
    package_dir = _write_package(tmp_path)
    report = d2_intake.evaluate_d2_package(package_dir)
    assert dict(report.counts) == BASELINE_COUNTS
    assert {row.field_id: row.state for row in report.results} == BASELINE
    assert report.complete is False
    assert report.exit_code == 1
    assert report.attestation_state == d2_intake.ATTESTATION_SYNTHETIC
    assert "evidence_class" not in report.as_dict()


def test_missing_package_directory_is_refused(tmp_path):
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.evaluate_d2_package(tmp_path / "does-not-exist")
    assert excinfo.value.reason == "D2_PACKAGE_NOT_FOUND"


# ---------------------------------------------------------------------------
# fail-closed package validity (exit 2)
# ---------------------------------------------------------------------------

def test_duplicate_field_id_is_refused(tmp_path):
    package_dir = _write_package(tmp_path)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    text = manifest.read_text(encoding="utf-8").replace(
        '"G0-D2-01": {', '"G0-D2-01": {"declared_status": "ABSENT"}, "G0-D2-01": {', 1)
    manifest.write_text(text, encoding="utf-8")
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_FIELD_ID_DUPLICATE"


def test_missing_field_id_is_refused(tmp_path):
    package_dir = _write_package(tmp_path)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    package = json.loads(manifest.read_text(encoding="utf-8"))
    del package["fields"]["G0-D2-30"]
    manifest.write_text(json.dumps(package), encoding="utf-8")
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_FIELD_ID_MISSING"


def test_unknown_field_id_is_refused(tmp_path):
    package_dir = _write_package(tmp_path)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    package = json.loads(manifest.read_text(encoding="utf-8"))
    package["fields"]["G0-D2-31"] = {"declared_status": "ABSENT"}
    manifest.write_text(json.dumps(package), encoding="utf-8")
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_FIELD_ID_UNKNOWN"


@pytest.mark.parametrize("digest", [ZERO_DIGEST, "", "abc", "A" * 64])
def test_placeholder_or_malformed_evidence_digest_refuses_package(digest, tmp_path):
    records = {"G0-D2-14": {"declared_status": "COMPLETE",
                            "evidence": [{"artifact": "reviewers.json", "digest": digest}]}}
    package_dir = _write_package(tmp_path, records=records)
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_PLACEHOLDER_EVIDENCE"


@pytest.mark.parametrize("artifact", [
    "/etc/hostname",
    "../outside.json",
    "media/interview.mp4",
    "media/interview.MOV",
    "audio/take.wav",
])
def test_media_or_escaping_evidence_path_refuses_package(artifact, tmp_path):
    records = {"G0-D2-01": {"declared_status": "COMPLETE",
                            "evidence": [{"artifact": artifact, "digest": "a" * 64}]}}
    package_dir = _write_package(tmp_path, records=records)
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason in {"D2_MEDIA_PATH_DECLARED", "D2_PACKAGE_PATH_ESCAPE"}


@pytest.mark.parametrize("status", ["AUTHORIZED", "GRANTED", "FROZEN", "PASS"])
def test_authorization_claim_in_declared_status_refuses_package(status, tmp_path):
    records = {"G0-D2-25": {"declared_status": status}}
    package_dir = _write_package(tmp_path, records=records)
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_AUTHORIZATION_CLAIMED"


@pytest.mark.parametrize("extra", [
    {"d3_grant": "D3-AUTH-1"},
    {"execution_authorized": True},
    {"owner_approval_claimed": True},
])
def test_smuggled_authorization_field_refuses_package(extra, tmp_path):
    records = {"G0-D2-25": {"declared_status": "ABSENT", **extra}}
    package_dir = _write_package(tmp_path, records=records)
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_AUTHORIZATION_CLAIMED"


def test_synthetic_marker_must_match_attester_kind(tmp_path):
    package_dir = _write_package(tmp_path, fixture=True, attester_kind="OWNER_SIGNED")
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_ATTESTATION_INVALID"


def test_wrong_schema_version_is_refused(tmp_path):
    package_dir = _write_package(tmp_path)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    package = json.loads(manifest.read_text(encoding="utf-8"))
    package["schema_version"] = "gate0.d2-intake-package.v0"
    manifest.write_text(json.dumps(package), encoding="utf-8")
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_PACKAGE_SCHEMA_MISMATCH"


# ---------------------------------------------------------------------------
# synthetic evidence never becomes VERIFIED real-Owner evidence
# ---------------------------------------------------------------------------

def test_complete_synthetic_package_passes_checks_but_never_verifies(tmp_path):
    package_dir = _write_package(tmp_path, records=_complete_records(), fixture=True)
    report = d2_intake.evaluate_d2_package(package_dir)
    by_id = {row.field_id: row for row in report.results}
    for field_id in _complete_records():
        assert by_id[field_id].validator_check == "VALID", field_id
        assert by_id[field_id].state == "PENDING", field_id
        assert d2_intake.D2_REASON_SYNTHETIC in by_id[field_id].reasons
    assert report.counts["VERIFIED"] == 0
    assert report.complete is False
    assert report.exit_code == 1
    assert report.attestation_state == d2_intake.ATTESTATION_SYNTHETIC
    assert "evidence_class" not in report.as_dict()
    assert report.owner_approval_claimed is False


def test_owner_signed_declaration_can_validate_but_is_never_authenticated(tmp_path):
    package_dir = _write_package(tmp_path, records=_complete_records(), fixture=False)
    report = d2_intake.evaluate_d2_package(package_dir)
    by_id = {row.field_id: row for row in report.results}
    assert by_id["G0-D2-10"].validator_check == "VALID"
    assert by_id["G0-D2-10"].state == "PENDING"
    assert "DECLARED_EVIDENCE_NOT_AUTHENTICATED" in by_id["G0-D2-10"].reasons
    assert report.counts == {"VERIFIED": 0, "PENDING": 7, "BLOCKED": 21, "NOT_OBSERVED": 2}
    assert all(row.state != "VERIFIED" for row in report.results)
    assert report.attestation_state == d2_intake.ATTESTATION_DECLARED
    assert report.authenticity == "DECLARED_NOT_AUTHENTICATED"
    assert report.complete is False  # 21 BLOCKED + 2 NOT_OBSERVED remain
    assert report.exit_code == 1


def test_report_never_emits_authorization_vocabulary(tmp_path):
    package_dir = _write_package(tmp_path, records=_complete_records(), fixture=False)
    report = d2_intake.evaluate_d2_package(package_dir)
    rendered_json = d2_intake.render_report_json(report)
    rendered_md = d2_intake.render_report_markdown(report)
    forbidden = ("AUTHORIZED", "GRANTED", "FROZEN", "PASS")
    assert {row.state for row in report.results}.isdisjoint(forbidden)
    for bad in forbidden:
        assert f'"state": "{bad}"' not in rendered_json
        assert f"| {bad} |" not in rendered_md
    assert "D-3" in rendered_md and "NOT_AUTHORIZED" in rendered_md


# ---------------------------------------------------------------------------
# precedence: BLOCKED over PENDING, observation-only over completion claims
# ---------------------------------------------------------------------------

def test_blocked_row_ignores_completion_claim(tmp_path):
    records = {"G0-D2-13": {"declared_status": "COMPLETE",
                            "evidence": [{"artifact": "editor-queries.json",
                                          "digest": "<computed>"}]}}
    package_dir = _write_package(tmp_path, records=records)
    report = d2_intake.evaluate_d2_package(package_dir)
    by_id = {row.field_id: row for row in report.results}
    assert by_id["G0-D2-13"].state == "BLOCKED"
    assert by_id["G0-D2-13"].unresolved_ruling == "R-11"


@pytest.mark.parametrize("field_id", ["G0-D2-18", "G0-D2-19"])
def test_observation_only_row_is_never_verified(field_id, tmp_path):
    records = {field_id: {"declared_status": "COMPLETE"}}
    package_dir = _write_package(tmp_path, records=records)
    report = d2_intake.evaluate_d2_package(package_dir)
    by_id = {row.field_id: row for row in report.results}
    assert by_id[field_id].state == "NOT_OBSERVED"
    assert d2_intake.D2_REASON_OBSERVATION in by_id[field_id].reasons


# ---------------------------------------------------------------------------
# deterministic per-field validators on real canonical helpers
# ---------------------------------------------------------------------------

def _state(tmp_path, field_id, records):
    package_dir = _write_package(tmp_path, records=records, fixture=False)
    report = d2_intake.evaluate_d2_package(package_dir)
    return {row.field_id: row for row in report.results}[field_id]


def test_editor_query_count_23_positives_fails(tmp_path):
    document = _editor_queries()
    index = next(i for i, row in enumerate(document["queries"]) if row["presence"] == "POSITIVE")
    del document["queries"][index]
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = document
    package_dir = _write_package(tmp_path, records={"G0-D2-10": _record("editor-queries.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-10"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_editor_query_count_25_positives_fails(tmp_path):
    document = _editor_queries()
    document["queries"].append(dict(document["queries"][0], query_id="q_extra"))
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = document
    package_dir = _write_package(tmp_path, records={"G0-D2-10": _record("editor-queries.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-10"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_editor_query_missing_family_fails(tmp_path):
    document = _editor_queries(per_family=0)
    for family in FAMILIES[:-1]:
        for index in range(6):
            document["queries"].append({
                "query_id": f"q_eval_{family.lower()}_{index}",
                "text": f"editor query {family} {index}",
                "family": family,
                "presence": "POSITIVE",
                "split": "EVALUATION",
            })
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = document
    package_dir = _write_package(tmp_path, records={"G0-D2-10": _record("editor-queries.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-10"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_absent_split_must_be_eight(tmp_path):
    passing = _state(tmp_path / "eight", "G0-D2-11",
                     {"G0-D2-11": _record("editor-queries.json")})
    assert passing.validator_check == "VALID"
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = _editor_queries(presence_counts={"ABSENT": 7})
    package_dir = _write_package(tmp_path / "seven",
                                 records={"G0-D2-11": _record("editor-queries.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-11"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_development_split_must_be_eight(tmp_path):
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = _editor_queries(dev_count=7)
    package_dir = _write_package(tmp_path, records={"G0-D2-12": _record("editor-queries.json")},
                                 artifacts=artifacts)
    report = d2_intake.evaluate_d2_package(package_dir)
    row = {r.field_id: r for r in report.results}["G0-D2-12"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_duplicate_query_identity_fails_closed(tmp_path):
    document = _editor_queries()
    document["queries"][1] = dict(document["queries"][0])
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = document
    package_dir = _write_package(tmp_path, records={"G0-D2-10": _record("editor-queries.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-10"]
    assert row.validator_check == "INVALID"
    assert any("AUTHORIZED_EDITOR_QUERIES" in reason for reason in row.reasons)


def test_reviewer_count_must_be_two_distinct(tmp_path):
    artifacts = dict(ARTIFACTS)
    artifacts["reviewers.json"] = _reviewers(("reviewer_a", "reviewer_a"))
    package_dir = _write_package(tmp_path, records={"G0-D2-14": _record("reviewers.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-14"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_placeholder_owner_id_cannot_close_owner_binding(tmp_path):
    artifacts = dict(ARTIFACTS)
    artifacts["owner-binding.json"] = _owner_binding("gate0-owner")
    package_dir = _write_package(tmp_path, records={"G0-D2-26": _record("owner-binding.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-26"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_duplicate_blinding_arm_rejected(tmp_path):
    artifacts = dict(ARTIFACTS)
    artifacts["blinding.json"] = _blinding([
        {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
        {"blind_arm_token": "arm-a", "arm_id": "offline-development-arm"},
    ])
    package_dir = _write_package(tmp_path, records={"G0-D2-17": _record("blinding.json")},
                                 artifacts=artifacts)
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-17"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


def test_evidence_digest_must_match_artifact(tmp_path):
    package_dir = _write_package(tmp_path)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    package = json.loads(manifest.read_text(encoding="utf-8"))
    package["fields"]["G0-D2-14"] = {
        "declared_status": "COMPLETE",
        "evidence": [{"artifact": "reviewers.json", "digest": "b" * 64}],
    }
    manifest.write_text(json.dumps(package), encoding="utf-8")
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-14"]
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"
    assert d2_intake.D2_REASON_DIGEST_MISMATCH in row.reasons


def test_declared_complete_without_evidence_stays_pending(tmp_path):
    records = {"G0-D2-14": {"declared_status": "COMPLETE", "evidence": []}}
    row = _state(tmp_path, "G0-D2-14", records)
    assert row.state == "PENDING"
    assert row.validator_check == "INVALID"


# ---------------------------------------------------------------------------
# source/media isolation: validator reads the package, nothing else
# ---------------------------------------------------------------------------

def test_validator_needs_no_access_outside_package_dir(tmp_path, monkeypatch):
    package_dir = _write_package(tmp_path, records=_complete_records(), fixture=False)
    _install_package_only_guard(monkeypatch, package_dir)
    report = d2_intake.evaluate_d2_package(package_dir)
    assert report.counts["PENDING"] + report.counts["VERIFIED"] == 7


def test_declared_media_reference_in_notes_is_never_resolved(tmp_path, monkeypatch):
    sentinel = tmp_path / "sentinel-media-root"
    sentinel.mkdir()
    (sentinel / "interview.mp4").write_bytes(b"not-real-media")
    package_dir = _write_package(tmp_path, records={
        "G0-D2-01": {"declared_status": "ABSENT",
                     "notes": f"declared owner root: {sentinel}/interview.mp4"},
    })
    real_stat = os.stat

    def guarded_stat(path, *args, **kwargs):
        if os.path.realpath(str(path)).startswith(str(sentinel)):
            raise AssertionError(f"validator resolved declared media path: {path}")
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(os, "stat", guarded_stat)
    # Review F1: an absolute media root in free-text notes now refuses the
    # package instead of being ignored, and it is still never resolved.
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.load_d2_package(package_dir)
    assert excinfo.value.reason == "D2_PACKAGE_PATH_ESCAPE"


# ---------------------------------------------------------------------------
# determinism and rendering
# ---------------------------------------------------------------------------

def test_identical_input_is_byte_identical_output(tmp_path):
    package_dir = _write_package(tmp_path, records=_complete_records())
    first = d2_intake.render_report_json(d2_intake.evaluate_d2_package(package_dir))
    second = d2_intake.render_report_json(d2_intake.evaluate_d2_package(package_dir))
    assert first == second
    assert first.endswith("\n")
    json.loads(first)


def test_report_digest_is_stable_across_key_order(tmp_path):
    package_dir = _write_package(tmp_path)
    baseline = d2_intake.evaluate_d2_package(package_dir)
    manifest = package_dir / d2_intake.D2_PACKAGE_FILE
    package = json.loads(manifest.read_text(encoding="utf-8"))
    package = {key: package[key] for key in reversed(list(package))}
    manifest.write_text(json.dumps(package, indent=4), encoding="utf-8")
    reordered = d2_intake.evaluate_d2_package(package_dir)
    assert reordered.package_digest == baseline.package_digest
    assert reordered.counts == baseline.counts


def test_markdown_report_lists_all_thirty_rows_and_warns(tmp_path):
    package_dir = _write_package(tmp_path)
    markdown = d2_intake.render_report_markdown(d2_intake.evaluate_d2_package(package_dir))
    for field_id in BASELINE:
        assert field_id in markdown
    assert "synthetic" in markdown.lower()
    assert "NOT_AUTHORIZED" in markdown
    assert "VERIFIED" in markdown


# ---------------------------------------------------------------------------
# CLI contract
# ---------------------------------------------------------------------------

def test_cli_exit_1_for_incomplete_package(tmp_path, capsys):
    cli = _load_cli()
    package_dir = _write_package(tmp_path)
    assert cli.main(["--package", str(package_dir), "--format", "json"]) == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["counts"] == BASELINE_COUNTS


def test_cli_exit_2_for_refused_package(tmp_path, capsys):
    cli = _load_cli()
    records = {"G0-D2-25": {"declared_status": "AUTHORIZED"}}
    package_dir = _write_package(tmp_path, records=records)
    assert cli.main(["--package", str(package_dir), "--format", "json"]) == 2
    output = capsys.readouterr()
    payload = json.loads(output.out)
    assert payload["error"]["reason"] == "D2_AUTHORIZATION_CLAIMED"
    assert "Traceback" not in output.err


def test_cli_markdown_format(tmp_path, capsys):
    cli = _load_cli()
    package_dir = _write_package(tmp_path)
    assert cli.main(["--package", str(package_dir), "--format", "markdown"]) == 1
    assert "| G0-D2-01 |" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# independent-review hardening: free-text claims, symlinks, artifact integrity
# ---------------------------------------------------------------------------

def _refused_reason(package_dir):
    with pytest.raises(d2_intake.D2IntakeError) as excinfo:
        d2_intake.evaluate_d2_package(package_dir)
    return excinfo.value.reason


def test_authorization_claim_in_notes_is_refused(tmp_path):
    records = {"G0-D2-25": {
        "declared_status": "PARTIAL",
        "notes": "This package GRANTS D-3-AUTH-1 and the owner approved execution.",
    }}
    package_dir = _write_package(tmp_path, records=records)
    assert _refused_reason(package_dir) == "D2_AUTHORIZATION_CLAIMED"


def test_d3_grant_token_in_package_notes_is_refused(tmp_path):
    package_dir = _write_package(tmp_path, extra={"notes": "see d3-auth-2 for reviewer access"})
    assert _refused_reason(package_dir) == "D2_AUTHORIZATION_CLAIMED"


def test_absolute_media_root_in_notes_is_refused(tmp_path):
    records = {"G0-D2-28": {
        "declared_status": "PARTIAL",
        "notes": "real root: /Users/owner/secret-corpus/clip.mp4",
    }}
    package_dir = _write_package(tmp_path, records=records)
    assert _refused_reason(package_dir) == "D2_PACKAGE_PATH_ESCAPE"


def test_d3_claim_inside_referenced_artifact_key_is_refused(tmp_path):
    reviewers = _reviewers()
    reviewers["d3_authorization"] = "GRANTED D3-AUTH-1"
    artifacts = dict(ARTIFACTS)
    artifacts["reviewers.json"] = reviewers
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    assert _refused_reason(package_dir) == "D2_AUTHORIZATION_CLAIMED"


def test_absolute_root_inside_referenced_artifact_value_is_refused(tmp_path):
    reviewers = _reviewers()
    reviewers["sample"] = "/Users/owner/secret-corpus/interview.mkv"
    artifacts = dict(ARTIFACTS)
    artifacts["reviewers.json"] = reviewers
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    assert _refused_reason(package_dir) == "D2_PACKAGE_PATH_ESCAPE"


def test_media_suffix_inside_referenced_artifact_value_is_refused(tmp_path):
    reviewers = _reviewers()
    reviewers["sample_name"] = "interview.mp4"
    artifacts = dict(ARTIFACTS)
    artifacts["reviewers.json"] = reviewers
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    assert _refused_reason(package_dir) == "D2_MEDIA_PATH_DECLARED"


def test_free_text_query_values_are_not_treated_as_claims(tmp_path):
    editor = _editor_queries()
    editor["queries"][0]["text"] = "the authorized visitor walks through the authorized area"
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = editor
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    report = d2_intake.evaluate_d2_package(package_dir)
    assert report.counts["PENDING"] == 7
    assert report.counts["BLOCKED"] == 21


def test_symlink_artifact_escaping_package_is_refused(tmp_path):
    package_dir = _write_package(tmp_path, records={"G0-D2-14": {
        "declared_status": "COMPLETE",
        "evidence": [{"artifact": "reviewers.json", "digest": "b" * 64}],
    }})
    outside = tmp_path / "outside-reviewers.json"
    outside.write_text(json.dumps(_reviewers()), encoding="utf-8")
    artifact = package_dir / "reviewers.json"
    artifact.unlink()
    artifact.symlink_to(outside)
    assert _refused_reason(package_dir) == "D2_PACKAGE_PATH_ESCAPE"


def test_directory_artifact_is_refused_with_specific_reason(tmp_path):
    package_dir = _write_package(tmp_path, records={"G0-D2-14": _record("reviewers.json")})
    artifact = package_dir / "reviewers.json"
    artifact.unlink()
    artifact.mkdir()
    assert _refused_reason(package_dir) == "D2_ARTIFACT_INVALID"


def test_duplicate_members_in_artifact_json_are_refused(tmp_path):
    package_dir = _write_package(tmp_path, records={"G0-D2-14": _record("reviewers.json")})
    artifact = package_dir / "reviewers.json"
    text = artifact.read_text(encoding="utf-8").replace(
        '"schema_version": "gate0.d2-reviewers.v1",',
        '"schema_version": "gate0.d2-reviewers.v1", "schema_version": "gate0.d2-reviewers.v1",',
        1,
    )
    artifact.write_text(text, encoding="utf-8")
    assert _refused_reason(package_dir) == "D2_ARTIFACT_INVALID"


def test_absent_declaration_with_evidence_stays_pending(tmp_path):
    package_dir = _write_package(tmp_path, artifacts=None, fixture=False, records={"G0-D2-14": {
        "declared_status": "ABSENT",
        "evidence": [{"artifact": "reviewers.json", "digest": "<computed>"}],
    }})
    row = {r.field_id: r for r in d2_intake.evaluate_d2_package(package_dir).results}["G0-D2-14"]
    assert row.state == "PENDING"
    assert d2_intake.D2_REASON_DECLARATION_INCONSISTENT in row.reasons


# --- Round 2 re-review hardening (N1-N4, N6) ---------------------------------


def test_grant_claim_in_free_text_artifact_value_is_refused(tmp_path):
    """N1: free-text prose cannot smuggle an explicit D-3 grant claim."""

    editor = _editor_queries()
    editor["queries"][0]["text"] = (
        "the owner has granted execution authorization for the real corpus"
    )
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = editor
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    assert _refused_reason(package_dir) == "D2_AUTHORIZATION_CLAIMED"


def test_absolute_media_path_as_artifact_mapping_key_is_refused(tmp_path):
    """N2: a mapping *key* may not be an absolute media path."""

    reviewers = _reviewers()
    reviewers["/Users/owner/secret-corpus/interview.mp4"] = True
    artifacts = dict(ARTIFACTS)
    artifacts["reviewers.json"] = reviewers
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    assert _refused_reason(package_dir) == "D2_PACKAGE_PATH_ESCAPE"


def test_glued_absolute_path_in_notes_is_refused(tmp_path):
    """N3: ``root=/Users/x/y`` is still an absolute path."""

    records = {"G0-D2-28": {
        "declared_status": "PARTIAL",
        "notes": "root=/Users/owner/secret-corpus",
    }}
    package_dir = _write_package(tmp_path, records=records)
    assert _refused_reason(package_dir) == "D2_PACKAGE_PATH_ESCAPE"


def test_nested_duplicate_members_in_artifact_json_are_refused(tmp_path):
    """N4: duplicate detection must recurse into nested objects."""

    package_dir = _write_package(tmp_path, records={"G0-D2-01": _record("corpus-designation.json")})
    artifact = package_dir / "corpus-designation.json"
    text = artifact.read_text(encoding="utf-8").replace(
        '"session_id": "sess_0",',
        '"session_id": "sess_0", "session_id": "sess_1",',
        1,
    )
    artifact.write_text(text, encoding="utf-8")
    assert _refused_reason(package_dir) == "D2_ARTIFACT_INVALID"


def test_benign_prose_with_authorization_words_is_not_refused(tmp_path):
    """N6: narrowing keeps ordinary prose from being treated as a grant claim."""

    records = {"G0-D2-02": {
        "declared_status": "PARTIAL",
        "notes": "corpus approved for use; authorized local corpus declaration",
    }}
    editor = _editor_queries()
    editor["queries"][0]["text"] = "the authorized visitor approved the room layout"
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = editor
    package_dir = _write_package(tmp_path, records=records, artifacts=artifacts,
                                 fixture=True)
    report = d2_intake.evaluate_d2_package(package_dir)
    assert report.counts["BLOCKED"] == 21
    assert report.counts["PENDING"] == 7


def test_d3_token_as_artifact_mapping_key_is_refused(tmp_path):
    """N7: a D-3 token used as a mapping key is still an authorization claim."""

    reviewers = _reviewers()
    reviewers["d-3-auth-1"] = "GRANTED"
    artifacts = dict(ARTIFACTS)
    artifacts["reviewers.json"] = reviewers
    package_dir = _write_package(tmp_path, records=_complete_records(), artifacts=artifacts)
    assert _refused_reason(package_dir) == "D2_AUTHORIZATION_CLAIMED"


def test_execution_worded_benign_prose_is_not_refused(tmp_path):
    """N8: operation words in ordinary prose are not an authorization claim."""

    editor = _editor_queries()
    editor["queries"][0]["text"] = (
        "the authorized stunt coordinator approved the execution of the jump"
    )
    artifacts = dict(ARTIFACTS)
    artifacts["editor-queries.json"] = editor
    records = {"G0-D2-02": {
        "declared_status": "PARTIAL",
        "notes": "owner approved the execution environment",
    }}
    package_dir = _write_package(tmp_path, records=records, artifacts=artifacts)
    report = d2_intake.evaluate_d2_package(package_dir)
    assert report.counts["BLOCKED"] == 21
    assert report.counts["PENDING"] == 7
