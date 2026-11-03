"""D-PROV-1 temporal-authority closure tests for the REAL preparation boundary."""
from __future__ import annotations

import hashlib
import json
import pathlib
import copy
from collections.abc import Mapping
from pathlib import Path
from types import SimpleNamespace

import pytest

import gate3.authority as _gate3_authority

from vip_fvs.real_source_probe import RealSourceProbeBinding
from vip_fvs.real_source_service import RealSourcePreparationRefusal, _source_pts_interval

PROBE_TB = (1, 1000)

# Sentinel: distinguishes "field omitted entirely" from "field present but None".
_MISSING = object()
_NO_REQUEST = object()


def _refine_named_source(tmp_path: Path, request_identity=_NO_REQUEST, *, source_revision_id="rev-refinement-1",
                         variant_tag=b"", table_time_base=None):
    """Build a deterministic local container and refine its measured PTS directly."""
    from gate3.container import parse_iso_bmff_timing
    from gate3.fixturegen import build_mp4
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import refine

    tmp_path.mkdir(parents=True, exist_ok=True)
    source = tmp_path / "refinement-source.mp4"
    source.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12),
                                 variant_tag=variant_tag))
    measured = parse_iso_bmff_timing(source)
    source_digest = hashlib.sha256(source.read_bytes()).hexdigest()
    record = refine(
        PtsTable(TimeBase(*(table_time_base or (1, measured["media_timescale"]))),
                 tuple(measured["pts_ticks"])),
        (0, 13),
        attempt_id="attempt-refinement-1",
        tool_identity={"tool": "synthetic-test"},
        time_domain="source_pts",
        precision="source-pts",
        source_revision_id=source_revision_id,
        source_content_digest=source_digest,
        stream_index=measured["stream_index"],
        container_path=str(source),
        request_identity=(
            None if request_identity is _NO_REQUEST else (
                request_identity if not request_identity or set(request_identity).issubset({"request_id"}) else
                _identity_for_measured_request(
                    request_identity, source_revision_id=source_revision_id,
                    source_locator=str(source), source_digest=source_digest,
                    stream_index=measured["stream_index"], start_pts=0, end_pts=13,
                )
            )
        ),
    )
    return record, source


def test_refine_requires_canonical_source_native_timebase_at_byte_admission(tmp_path: Path) -> None:
    record, _ = _refine_named_source(
        tmp_path, _valid_refinement_request_identity(), table_time_base=(2, 25)
    )

    assert record.get("blocked") == "TIME_BASE_DOES_NOT_MATCH_NAMED_BYTES"


@pytest.mark.parametrize("time_base", [
    {"num": 2, "den": 25},
    {"num": 2, "den": 50},
    {"num": 1, "den": 50},
    {"den": 25},
    {"num": True, "den": 25},
    {"num": 0, "den": 25},
    {"num": -1, "den": 25},
])
def test_binding_predicate_rejects_noncanonical_record_timebase_even_with_recomputed_digest(
    tmp_path: Path, time_base
) -> None:
    from gate3.refinement import is_binding_eligible

    record, _ = _refine_named_source(tmp_path, _valid_refinement_request_identity())
    changed = json.loads(json.dumps(record))
    changed["time_base"] = time_base
    changed["evidence_digest"] = _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, changed
    )

    assert not is_binding_eligible(changed)


def test_equivalent_unreduced_request_timebase_matches_canonical_measured_record(tmp_path: Path) -> None:
    from gate3.refinement import is_binding_eligible

    record, _ = _refine_named_source(
        tmp_path,
        _valid_refinement_request_identity(expected_timebase=[2, 50]),
    )

    assert record["time_base"] == {"num": 1, "den": 25}
    assert is_binding_eligible(record)


def test_binding_reverification_rejects_altered_persisted_measurement_artifact(tmp_path: Path) -> None:
    from gate3.container import parse_iso_bmff_timing
    from gate3.fixturegen import build_mp4
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import is_binding_eligible, refine

    source = tmp_path / "artifact-backed-source.mp4"
    source.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12)))
    facts = parse_iso_bmff_timing(source)
    artifact_path = tmp_path / "measurement.json"
    artifact_path.write_text(json.dumps({**facts, "source_path": str(source.resolve())}))
    identity = _identity_for_measured_request(
        _valid_refinement_request_identity(), source_revision_id="rev-refinement-1",
        source_locator=str(source), source_digest=facts["source_bytes_sha256"],
        stream_index=facts["stream_index"], start_pts=0, end_pts=13,
    )
    record = refine(
        PtsTable(TimeBase(1, facts["media_timescale"]), tuple(facts["pts_ticks"])), (0, 13),
        attempt_id="attempt-refinement-1", tool_identity={"tool": "synthetic-test"},
        time_domain="source_pts", precision="source-pts", source_revision_id="rev-refinement-1",
        source_content_digest=facts["source_bytes_sha256"], stream_index=facts["stream_index"],
        measurement_artifact_path=str(artifact_path), request_identity=identity,
    )
    assert is_binding_eligible(record)

    artifact = json.loads(artifact_path.read_text())
    artifact["media_timescale"] = 50
    artifact_path.write_text(json.dumps(artifact))

    assert not is_binding_eligible(record)


def test_vfr_source_pts_keep_measured_timebase_and_ticks(tmp_path: Path) -> None:
    from gate3.container import parse_iso_bmff_timing
    from gate3.fixturegen import build_mp4
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import BINDING_CHECK, is_binding_eligible, refine

    source = tmp_path / "vfr-source.mp4"
    source.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 80, 120, 40)))
    facts = parse_iso_bmff_timing(source)
    identity = _identity_for_measured_request(
        _valid_refinement_request_identity(), source_revision_id="rev-refinement-1",
        source_locator=str(source), source_digest=facts["source_bytes_sha256"],
        stream_index=facts["stream_index"], start_pts=80, end_pts=280,
    )
    record = refine(
        PtsTable(TimeBase(1, facts["media_timescale"]), tuple(facts["pts_ticks"])), (80, 280),
        attempt_id="attempt-refinement-1", tool_identity={"tool": "synthetic-test"},
        time_domain="source_pts", precision="source-pts", source_revision_id="rev-refinement-1",
        source_content_digest=facts["source_bytes_sha256"], stream_index=facts["stream_index"],
        container_path=str(source), request_identity=identity, declared_rate=25,
    )
    binding = next(item for item in record["validation_results"] if item.get("check") == BINDING_CHECK)

    assert record["time_base"] == {"num": 1, "den": 1000}
    assert tuple(binding["pts_ticks"]) == (0, 40, 80, 160, 280)
    assert is_binding_eligible(record)


def _valid_refinement_request_identity(**overrides):
    payload = {
        "request_id": "request-refinement-1",
        "candidate_assertion_ref": "assertion-refinement-1",
        "source_revision_id": "rev-refinement-1",
        "source_locator": "source.mp4",
        "expected_source_sha256": "b" * 64,
        "selected_stream_index": 0,
        "requested_start_pts": 0,
        "requested_end_pts": 13,
        "producer_attempt_id": "attempt-refinement-1",
        "idempotency_key": "idem-refinement-1",
        "expected_timebase": None,
    }
    payload.update({key: value for key, value in overrides.items() if key in payload})
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return {
        "request_id": payload["request_id"],
        "candidate_assertion_ref": payload["candidate_assertion_ref"],
        "producer_attempt_id": payload["producer_attempt_id"],
        "idempotency_key": payload["idempotency_key"],
        "request_digest": digest,
        "request": payload,
        **{key: value for key, value in overrides.items() if key not in payload},
    }


def _identity_for_measured_request(identity, *, source_revision_id, source_locator,
                                   source_digest, stream_index, start_pts, end_pts):
    default = _valid_refinement_request_identity()["request"]
    request_overrides = {
        key: value for key, value in identity.get("request", {}).items()
        if key in default and value != default[key]
    }
    payload = {
        **default,
        "source_revision_id": source_revision_id,
        "source_locator": source_locator,
        "expected_source_sha256": source_digest,
        "selected_stream_index": stream_index,
        "requested_start_pts": start_pts,
        "requested_end_pts": end_pts,
        **request_overrides,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    result = {
        "request_id": payload["request_id"],
        "candidate_assertion_ref": payload["candidate_assertion_ref"],
        "producer_attempt_id": payload["producer_attempt_id"],
        "idempotency_key": payload["idempotency_key"],
        "request_digest": digest,
        "request": payload,
    }
    for key in ("request_id", "candidate_assertion_ref", "producer_attempt_id", "idempotency_key", "request_digest"):
        if key in identity and key != "request_digest":
            result[key] = identity[key]
    supplied_digest = identity.get("request_digest")
    if (isinstance(supplied_digest, str)
            and (len(supplied_digest) != 64 or any(ch not in "0123456789abcdef" for ch in supplied_digest))):
        result["request_digest"] = supplied_digest
    return result


def test_omitted_request_identity_cannot_emit_binding_measured_evidence(tmp_path: Path) -> None:
    from gate3.refinement import is_binding_eligible

    record, _ = _refine_named_source(tmp_path)

    assert not is_binding_eligible(record)
    assert record.get("binding_eligible") is False or record.get("blocked")


@pytest.mark.parametrize("identity", [
    {},
    {"request_id": "only-one-field"},
    _valid_refinement_request_identity(request_digest="not-a-digest"),
])
def test_malformed_request_identity_refuses(tmp_path: Path, identity) -> None:
    record, _ = _refine_named_source(tmp_path, identity)

    assert record.get("blocked") in {
        "REFINEMENT_REQUEST_IDENTITY_INVALID",
        "REFINEMENT_REQUEST_DIGEST_INVALID",
    }
    assert record.get("binding_eligible") is not True


def test_request_identity_producer_attempt_must_match(tmp_path: Path) -> None:
    record, _ = _refine_named_source(
        tmp_path,
        _valid_refinement_request_identity(producer_attempt_id="different-attempt"),
    )

    assert record.get("blocked") == "REFINEMENT_REQUEST_ATTEMPT_MISMATCH"


@pytest.mark.parametrize("field,value", [
    ("source_revision_id", "different-revision"),
    ("expected_source_sha256", "c" * 64),
    ("selected_stream_index", 1),
    ("requested_end_pts", 25),
])
def test_request_commitment_must_match_measured_c2_inputs(tmp_path: Path, field, value) -> None:
    identity = _valid_refinement_request_identity(**{field: value})

    record, _ = _refine_named_source(tmp_path, identity)

    assert record.get("blocked") == "REFINEMENT_REQUEST_C2_MISMATCH"
    assert record.get("binding_eligible") is not True


def test_request_identity_is_in_c2_binding_and_evidence_digest(tmp_path: Path) -> None:
    from gate3.refinement import BINDING_CHECK

    record, _ = _refine_named_source(tmp_path, _valid_refinement_request_identity())
    binding = next(
        item for item in record["validation_results"]
        if item.get("check") == BINDING_CHECK
    )

    assert binding["request_identity"]["request"]["expected_source_sha256"] == record["source_content_digest"]
    assert binding["request_identity"]["request"]["requested_start_pts"] == record["start_ticks"]
    assert binding["request_identity"]["request"]["requested_end_pts"] == record["end_ticks"]
    assert _gate3_authority.assert_evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, record
    ) == record["evidence_digest"]
    changed = json.loads(json.dumps(record))
    changed_binding = next(
        item for item in changed["validation_results"]
        if item.get("check") == BINDING_CHECK
    )
    changed_binding["request_identity"]["request_id"] = "different-request"
    assert _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, changed
    ) != record["evidence_digest"]


def test_binding_predicate_rejects_evidence_without_request_identity(tmp_path: Path) -> None:
    from gate3.refinement import BINDING_CHECK, is_binding_eligible

    record, _ = _refine_named_source(tmp_path, _valid_refinement_request_identity())
    changed = json.loads(json.dumps(record))
    binding = next(
        item for item in changed["validation_results"]
        if item.get("check") == BINDING_CHECK
    )
    del binding["request_identity"]
    changed["evidence_digest"] = _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, changed
    )

    assert not is_binding_eligible(changed)


def test_binding_predicate_rejects_request_interval_mismatch(tmp_path: Path) -> None:
    from gate3.refinement import BINDING_CHECK, is_binding_eligible

    record, _ = _refine_named_source(tmp_path, _valid_refinement_request_identity())
    changed = json.loads(json.dumps(record))
    binding = next(
        item for item in changed["validation_results"]
        if item.get("check") == BINDING_CHECK
    )
    binding["request_identity"]["request"]["requested_end_pts"] = 25
    binding["request_identity"]["request_digest"] = hashlib.sha256(
        json.dumps(
            binding["request_identity"]["request"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    changed["evidence_digest"] = _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, changed
    )

    assert not is_binding_eligible(changed)


@pytest.mark.parametrize("locator_case", ["distinct_path", "nul_byte"])
def test_binding_predicate_rejects_request_locator_different_from_persisted_artifact_source(
    tmp_path: Path, locator_case: str,
) -> None:
    from gate3.container import parse_iso_bmff_timing
    from gate3.fixturegen import build_mp4
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import refine, is_binding_eligible

    source = tmp_path / "artifact-source.mp4"
    source.write_bytes(build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12)))
    facts = parse_iso_bmff_timing(source)
    artifact = {**facts, "source_path": str(source.resolve())}
    artifact_path = tmp_path / "measurement.json"
    artifact_path.write_text(json.dumps(artifact))
    request_source = tmp_path / "request-source.mp4"
    request_source.write_bytes(source.read_bytes())
    request_locator = (str(request_source.resolve()) if locator_case == "distinct_path"
                       else f"{tmp_path}/bad\x00locator.mp4")
    identity = _identity_for_measured_request(
        {"request": {"source_locator": request_locator}},
        source_revision_id="rev-refinement-1",
        source_locator=str(source.resolve()),
        source_digest=facts["source_bytes_sha256"],
        stream_index=facts["stream_index"], start_pts=0, end_pts=13,
    )
    identity["request"]["source_locator"] = request_locator
    identity["request_digest"] = hashlib.sha256(
        json.dumps(identity["request"], sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    record = refine(
        PtsTable(TimeBase(1, facts["media_timescale"]), tuple(facts["pts_ticks"])), (0, 13),
        attempt_id="attempt-refinement-1", tool_identity={"tool": "synthetic-test"},
        time_domain="source_pts", precision="source-pts", source_revision_id="rev-refinement-1",
        source_content_digest=facts["source_bytes_sha256"], stream_index=facts["stream_index"],
        measurement_artifact_path=str(artifact_path), request_identity=identity,
    )

    assert not record.get("blocked")
    assert not is_binding_eligible(record)


@pytest.mark.parametrize("invalid_time_base", [None, "1/25"])
def test_binding_predicate_rejects_invalid_measured_time_base_without_raising(
    tmp_path: Path, invalid_time_base,
) -> None:
    from gate3.refinement import is_binding_eligible

    identity = _valid_refinement_request_identity(expected_timebase=(1, 25))
    record, _ = _refine_named_source(tmp_path, identity)
    changed = json.loads(json.dumps(record))
    changed["time_base"] = invalid_time_base
    changed["evidence_digest"] = _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, changed
    )

    assert not is_binding_eligible(changed)


@pytest.mark.parametrize(
    ("invalid_time_base", "label"),
    [
        (None, "null_timebase"),
        ("1/25", "string_non_mapping"),
        ([1, 25], "list_non_mapping"),
        (25, "int_non_mapping"),
        ({}, "empty_mapping"),
        ({"num": 1}, "missing_den"),
        ({"den": 25}, "missing_num"),
        ({"num": 0, "den": 25}, "zero_num"),
        ({"num": -1, "den": 25}, "negative_num"),
        ({"num": 1, "den": 0}, "zero_den"),
        ({"num": 1, "den": -25}, "negative_den"),
        ({"num": True, "den": 25}, "bool_num"),
        ({"num": 1, "den": False}, "bool_den"),
        ({"num": 1.0, "den": 25}, "float_num"),
        ({"num": "1", "den": 25}, "str_num"),
        ({"other": 123}, "unrelated_keys_only"),
    ],
)
def test_binding_predicate_rejects_unconditional_invalid_measured_time_base_fail_closed(
    tmp_path: Path, invalid_time_base, label: str,
) -> None:
    from gate3.refinement import is_binding_eligible, is_structurally_eligible

    identity = _valid_refinement_request_identity(expected_timebase=None)
    record, _ = _refine_named_source(tmp_path, identity)
    assert is_binding_eligible(record), "baseline valid record must be binding eligible"

    changed = json.loads(json.dumps(record))
    changed["time_base"] = invalid_time_base
    changed["evidence_digest"] = _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, changed
    )

    assert not is_binding_eligible(changed)
    assert not is_structurally_eligible(changed)


def test_binding_predicate_unconditional_valid_timebase_and_rational_equivalence(
    tmp_path: Path,
) -> None:
    from gate3.refinement import is_binding_eligible, is_structurally_eligible

    # Case 6: valid measured timebase + expected_timebase absent/null -> remains eligible
    identity_no_expected = _valid_refinement_request_identity(expected_timebase=None)
    record, _ = _refine_named_source(tmp_path, identity_no_expected)
    assert is_binding_eligible(record)
    assert is_structurally_eligible(record)

    # Case 7a: valid equivalent rational comparison (e.g. 2/50 == 1/25) -> eligible
    identity_equiv = _valid_refinement_request_identity(expected_timebase=(2, 50))
    record_equiv, _ = _refine_named_source(tmp_path, identity_equiv)
    assert is_binding_eligible(record_equiv)
    assert is_structurally_eligible(record_equiv)

    # Case 7b: non-equivalent rational comparison (e.g. 1/30 != 1/25) -> ineligible
    identity_mismatch = _valid_refinement_request_identity(expected_timebase=(1, 30))
    record_mismatch, _ = _refine_named_source(tmp_path, identity_mismatch)
    assert not is_binding_eligible(record_mismatch)
    assert not is_structurally_eligible(record_mismatch)


def test_identical_refinement_request_is_deterministic(tmp_path: Path) -> None:
    identity = _valid_refinement_request_identity()
    first, _ = _refine_named_source(tmp_path, identity)
    second, _ = _refine_named_source(tmp_path, identity)

    assert first == second


def test_changed_request_identity_does_not_alias_refinement(tmp_path: Path) -> None:
    first, _ = _refine_named_source(tmp_path, _valid_refinement_request_identity())
    second, _ = _refine_named_source(
        tmp_path,
        _valid_refinement_request_identity(
            request_id="request-refinement-2"
        ),
    )

    assert first["refinement_id"] != second["refinement_id"]
    assert first["evidence_digest"] != second["evidence_digest"]


def test_changed_source_identity_does_not_alias_refinement(tmp_path: Path) -> None:
    identity = _valid_refinement_request_identity()
    first, _ = _refine_named_source(tmp_path / "source-a", identity)
    second, _ = _refine_named_source(
        tmp_path / "source-b", identity, source_revision_id="rev-refinement-2",
        variant_tag=b"different-source-bytes",
    )

    assert first["refinement_id"] != second["refinement_id"]
    assert first["source_content_digest"] != second["source_content_digest"]


def _source(tmp_path: Path) -> Path:
    path = tmp_path / "generated-source.mp4"
    path.write_bytes(b"generated fixture bytes")
    return path


def _byte_bound_source(tmp_path: Path) -> Path:
    """Build the exact local bytes required by the current C2 revalidation contract."""
    from gate3.fixturegen import build_mp4

    path = tmp_path / "byte-bound-generated-source.mp4"
    path.write_bytes(build_mp4(media_timescale=1000, sample_deltas=(40, 40, 40)))
    return path


def _byte_bound_refinement(probe: RealSourceProbeBinding) -> dict:
    """Produce a real C2-bound record for positive preparation-path guards."""
    from vip_fvs.refinement_adapter import refine_retrieval_candidate

    hit = SimpleNamespace(
        source_sha256=probe.source_sha256, source_path=str(probe.source_path),
        pts=40, timebase_num=probe.timebase_num, timebase_den=probe.timebase_den,
        rank=1, score=0.9,
    )
    result = refine_retrieval_candidate(
        hit, source_path=probe.source_path,
        source_revision_id=probe.source_revision_id, requested_pts=(40, 80),
        stream_index=probe.selected_stream_index,
        selected_stream_index=probe.selected_stream_index,
        attempt_id="attempt-tb-1", stage_idempotency_key="real-source:attempt-tb-1",
        tool_identity={"name": "vip_fvs.real_source_service", "version": "v3"},
    )
    assert result.binding_eligible
    return dict(result.measured_refinement)


def _probe(source: Path, run_dir: Path, *, frames=(), packets=(), pts_ticks=None) -> RealSourceProbeBinding:
    payload: dict = {
        "streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}],
        "stream_index": 0,
        "frames": [
            {"stream_index": 0, "best_effort_timestamp": str(t)} for t in frames
        ],
        "packets": [
            {"stream_index": 0, "pts": str(t)} for t in packets
        ],
    }
    if pts_ticks is not None:
        payload["pts_ticks"] = list(pts_ticks)
    return RealSourceProbeBinding(
        source_path=source,
        source_revision_id="rev-tb-1",
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_byte_count=source.stat().st_size,
        selected_stream_index=0,
        timebase_num=PROBE_TB[0],
        timebase_den=PROBE_TB[1],
        ffprobe_json=payload,
        probe_digest="c" * 64,
        probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        raw_probe_artifact_ref=str(run_dir / "probe-raw.json"),
        canonical_probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        policy_identity="policy-real-source-test",
    )


def _hit(*, pts: int, tb_num=_MISSING, tb_den=_MISSING) -> SimpleNamespace:
    fields = {
        "source_sha256": None, "source_path": None, "rank": 1, "score": 0.9,
        "pts": pts, "timestamp_human": "00:00:00.040",
    }
    if tb_num is not _MISSING:
        fields["timebase_num"] = tb_num
    if tb_den is not _MISSING:
        fields["timebase_den"] = tb_den
    return SimpleNamespace(**fields)


def test_locator_timebase_equal_to_probe_is_admissible(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["start"] == 40 and interval["end"] == 80
    assert interval["time_domain"] == "source_pts"
    assert interval["endpoint_semantics"] == "half_open"


def test_locator_timebase_rationally_equivalent_but_unreduced_is_admissible(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    interval = _source_pts_interval(_hit(pts=40, tb_num=2, tb_den=2000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


def test_locator_timebase_mismatch_refuses_before_reinterpretation(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_LOCATOR_TIMEBASE_MISMATCH"):
        _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=2000), probe)


@pytest.mark.parametrize("tb_num,tb_den,expected", [
    (_MISSING, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (1, _MISSING, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (None, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (True, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (0, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (1, -1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
])
def test_locator_timebase_invalid_refuses(tmp_path: Path, tb_num, tb_den, expected: str) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match=expected):
        _source_pts_interval(_hit(pts=40, tb_num=tb_num, tb_den=tb_den), probe)


def test_packet_only_tick_cannot_be_an_endpoint(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(120,))
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["end"] == 80


def test_packet_only_hit_tick_is_not_admissible(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(120,))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_PTS_NOT_OBSERVED"):
        _source_pts_interval(_hit(pts=120, tb_num=1, tb_den=1000), probe)


def test_same_tick_in_frame_and_packet_is_eligible_via_frame(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(80,))
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["end"] == 80


def test_top_level_pts_ticks_never_confers_endpoint_authority(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", pts_ticks=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED"):
        _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)


def test_alias_fallback_skips_malformed_earlier_alias(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run")
    probe = RealSourceProbeBinding(**{
        **probe.__dict__,
        "ffprobe_json": {
            "streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}],
            "stream_index": 0,
            "frames": [
                {"stream_index": 0, "best_effort_timestamp": "40.5", "pts": "40"},
                {"stream_index": 0, "best_effort_timestamp": None, "pts": "80"},
            ],
            "packets": [],
        },
    })
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


def test_no_authoritative_frame_evidence_refuses_distinctly(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", packets=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED"):
        _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)


def test_duplicate_presentation_ticks_are_preserved_in_the_authoritative_projection(tmp_path: Path) -> None:
    """§3.2(7): duplicates are evidence and must survive the projection itself.

    An interval-only assertion cannot discharge this: a set-collapsing
    implementation would still yield start=40, end=80.
    """
    from vip_fvs.real_source_service import _frame_presentation_pts

    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 40, 80))
    assert _frame_presentation_pts(probe) == (40, 40, 80)
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


def test_endpoint_selection_consumes_the_multiplicity_preserving_projection() -> None:
    """Guard: interval coordinates must be derived from the projection helper.

    If interval selection kept its own set-collapsing path, duplicate evidence
    would be dropped even though the projection preserved it.
    """
    import inspect
    import vip_fvs.real_source_service as service

    assert "_frame_presentation_pts" in inspect.getsource(service._source_pts_interval)


def test_non_selected_stream_frames_are_ignored(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    probe = RealSourceProbeBinding(**{
        **probe.__dict__,
        "ffprobe_json": {
            **probe.ffprobe_json,
            "frames": list(probe.ffprobe_json["frames"]) + [
                {"stream_index": 1, "best_effort_timestamp": "999"}
            ],
        },
    })
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["end"] == 80


def test_no_rate_field_is_consulted_for_endpoint_selection() -> None:
    import inspect
    import vip_fvs.real_source_service as service
    source_text = inspect.getsource(service)
    for forbidden in ("r_frame_rate", "avg_frame_rate", "nb_frames", "duration_ts"):
        assert forbidden not in source_text, f"nominal-rate field consulted: {forbidden}"


def test_refinement_request_is_closed_and_source_native() -> None:
    from dataclasses import FrozenInstanceError

    from gate3.refinement_request import RefinementRequest

    request = RefinementRequest(
        request_id="request-1",
        candidate_assertion_ref="assertion-1",
        source_revision_id="revision-1",
        source_locator="/tmp/source.mp4",
        expected_source_sha256="a" * 64,
        selected_stream_index=0,
        requested_start_pts=40,
        requested_end_pts=80,
        producer_attempt_id="attempt-1",
        idempotency_key="stage-key-1",
        expected_timebase=(1, 1000),
    )
    assert request.requested_start_pts == 40
    assert request.expected_timebase == (1, 1000)
    with pytest.raises(FrozenInstanceError):
        request.request_id = "changed"
    with pytest.raises(TypeError):
        RefinementRequest(
            request_id="request-1",
            candidate_assertion_ref="assertion-1",
            source_revision_id="revision-1",
            source_locator="/tmp/source.mp4",
            expected_source_sha256="a" * 64,
            selected_stream_index=0,
            requested_start_pts=40,
            requested_end_pts=80,
            producer_attempt_id="attempt-1",
            idempotency_key="stage-key-1",
            unexpected_field="closed",
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"requested_start_pts": True},
        {"requested_start_pts": 40.0},
        {"requested_end_pts": False},
        {"requested_end_pts": 80.0},
        {"requested_end_pts": 40},
        {"requested_end_pts": 39},
        {"expected_source_sha256": "not-a-digest"},
        {"source_revision_id": ""},
        {"source_locator": ""},
        {"candidate_assertion_ref": ""},
        {"selected_stream_index": True},
        {"selected_stream_index": -1},
        {"producer_attempt_id": ""},
        {"idempotency_key": ""},
        {"expected_timebase": (1, True)},
        {"expected_timebase": (0, 1000)},
    ],
)
def test_refinement_request_rejects_malformed_authority_inputs(overrides) -> None:
    from gate3.refinement_request import RefinementRequest

    values = {
        "request_id": "request-1",
        "candidate_assertion_ref": "assertion-1",
        "source_revision_id": "revision-1",
        "source_locator": "/tmp/source.mp4",
        "expected_source_sha256": "a" * 64,
        "selected_stream_index": 0,
        "requested_start_pts": 40,
        "requested_end_pts": 80,
        "producer_attempt_id": "attempt-1",
        "idempotency_key": "stage-key-1",
        "expected_timebase": None,
    }
    values.update(overrides)
    with pytest.raises((TypeError, ValueError)):
        RefinementRequest(**values)


# --------------------------------------------------------------------------
# D-PROV-1.C — pre-publication authoritative-refinement / probe timebase gate
# These exercise the full preparation path with deterministic synthetic bytes
# and a fake refinement adapter. No container parser is duplicated and no real
# media is touched: the adapter is injected, so the source is never parsed.
# --------------------------------------------------------------------------

def _runtime():
    import numpy as np
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.retrieval_adapter import fake_semantic_space

    return checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 768), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 768), dtype=np.float32),
        semantic_space=fake_semantic_space(), fake=False, runtime_identity="tb-gate-runtime",
    )


def _authorization(source: Path, index: Path, output: Path, runtime, query: str = "target") -> dict:
    import json as _json
    from persistent_local_index.model_space import semantic_space_id

    space = runtime.semantic_space
    body = {
        "authorization_id": "auth-tb", "source_path": str(source.resolve()),
        "source_revision_id": "rev-tb-1",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "purpose": "generated temporal-authority test fixture",
        "model_root": str((source.parent / "model").resolve()),
        "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256,
        "runtime_root": str((output.parent / "runtime").resolve()),
        "query_digest": hashlib.sha256(_json.dumps(query).encode()).hexdigest(),
        "model_identity": space.model_identity, "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256, "semantic_space_id": semantic_space_id(space),
        "index_root": str(index.resolve()),
        "index_digest": hashlib.sha256(_json.dumps(str(index)).encode()).hexdigest(),
        "output_root": str(output.resolve()),
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
        "local_only": True,
        "policy_digest": "1" * 64, "scope_digest": "2" * 64,
        "expires_at": "2099-01-01T00:00:00+00:00", "revoked": False,
        "selected_stream_index": 0,
    }
    body["record_digest"] = hashlib.sha256(
        _json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    return body


def _prepare(monkeypatch, tmp_path: Path, *, probe, measured: dict | None,
             output_root: Path | None = None, use_real_refinement: bool = False):
    """Run one full preparation with an injected measured refinement.

    A dictionary is injected for negative boundary cases.  ``None`` leaves the
    production adapter active for positive-path tests that cross E02's current
    byte-binding revalidation.  ``output_root`` exercises path-length boundaries.
    """
    from persistent_local_index.model_space import semantic_space_id as _space_id

    from vip_fvs.real_source_service import RealSourceRequest, prepare_real_source

    runtime = _runtime()
    index = tmp_path / "index"
    output = output_root if output_root is not None else tmp_path / "out"
    observed_probe = []

    def probe_snapshot(path, **kwargs):
        from dataclasses import replace
        bound = replace(
            probe, source_path=Path(path), source_locator=kwargs["source_locator"],
            snapshot_evidence=kwargs["snapshot_evidence"],
        )
        observed_probe.append(bound)
        return bound

    monkeypatch.setattr("vip_fvs.real_source_service.probe_real_source", probe_snapshot)
    monkeypatch.setattr(
        "vip_fvs.real_source_service.retrieve_local_semantic",
        lambda *a, **k: SimpleNamespace(
            space_id=_space_id(runtime.semantic_space),
            generation_id="tb-generation",
            hits=(SimpleNamespace(
            source_sha256=observed_probe[0].source_sha256, source_path=str(observed_probe[0].source_path),
                rank=1, score=0.9, pts=40, timebase_num=1, timebase_den=1000,
                timestamp_human="00:00:00.040",
            ),),
        ),
    )
    if measured is not None and not use_real_refinement:
        def injected_refinement(*args, **kwargs):
            record = copy.deepcopy(measured)
            binding = next((entry for entry in record.get("validation_results", ())
                            if isinstance(entry, dict) and entry.get("check") == "C2_named_byte_binding"), None)
            supplied_digest = record.get("evidence_digest")
            try:
                originally_valid = (
                    binding is not None
                    and _gate3_authority.assert_evidence_digest(
                        _gate3_authority.RECORD_KIND_REFINEMENT, record
                    ) == supplied_digest
                )
            except Exception:
                originally_valid = False
            if originally_valid:
                evidence = dict(kwargs["snapshot_evidence"])
                byte_authority = binding["byte_authority"]
                byte_authority["container_path"] = str(kwargs["source_path"])
                byte_authority["snapshot_evidence"] = evidence
                binding["origin"]["ref"] = str(kwargs["source_path"])
                identity = binding["request_identity"]
                request_identity = dict(identity["request"])
                request_identity["source_locator"] = str(kwargs["source_path"])
                identity["request"] = request_identity
                canonical_request = _gate3_authority.canonical_json(request_identity)
                identity["request_digest"] = hashlib.sha256(
                    canonical_request.encode("utf-8") if isinstance(canonical_request, str)
                    else canonical_request
                ).hexdigest()
                record["evidence_digest"] = _gate3_authority.evidence_digest(
                    _gate3_authority.RECORD_KIND_REFINEMENT, record
                )
                measured.clear()
                measured.update(record)
            return SimpleNamespace(measured_refinement=record, binding_eligible=True)

        monkeypatch.setattr(
            "vip_fvs.real_source_service.refine_retrieval_candidate",
            injected_refinement,
        )
    request = RealSourceRequest(
        source_path=probe.source_path, query="target",
        authorization=_authorization(probe.source_path, index, output, runtime),
        runtime=runtime, index_root=index, output_root=output, run_dir=tmp_path / "run",
        source_revision_id=probe.source_revision_id, attempt_id="attempt-tb-1",
        selected_stream_index=0, model_root=tmp_path / "model",
        source_snapshot_root=tmp_path / "snapshot-store",
        max_source_bytes=1_000_000, max_store_bytes=2_000_000,
    )
    return prepare_real_source(request)


def _measured_base(source: Path, *, time_base) -> dict:
    record = {
        "refinement_id": "ref-tb-1", "evidence_digest": "d" * 64,
        "source_revision_id": "rev-tb-1", "stream_index": 0,
        "source_content_digest": hashlib.sha256(source.read_bytes()).hexdigest(),
        "start_ticks": 40, "end_ticks": 80,
        "produced_by_gate3_refinement_attempt": True,
        "evidence_class": "MEASURED", "time_domain": "source_pts", "precision": "source-pts",
    }
    if time_base is not _MISSING:
        record["time_base"] = time_base
    # Put the placeholder digest in the shape Gate-3 actually emits so that
    # digest-shape guards and digest-projection tests stay separable.
    record["evidence_digest"] = _gate3_authority.evidence_digest(
        _gate3_authority.RECORD_KIND_REFINEMENT, record,
    )
    return record


def test_missing_measured_timebase_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base=_MISSING)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


@pytest.mark.parametrize("bad", [True, 1.5, "1/1000", None, {"num": 1, "den": 0}, {"num": 1}, {"num": 0, "den": 1000}])
def test_invalid_measured_timebase_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch, bad) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base=bad)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


def test_measured_timebase_mismatch_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 2000})
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


def test_matching_measured_timebase_is_published_as_authority(tmp_path: Path, monkeypatch) -> None:
    """POSITIVE_GUARD, not a RED case.

    Against pre-change code this passes vacuously: with measured and probe both
    ``1/1000``, the current implementation publishes the *probe* tuple and the
    values happen to match. Its role is to ensure the GREEN implementation still
    publishes successfully and that both published tuples equal the authoritative
    measured tuple. It is not evidence that the measured-timebase gate exists.

    The genuine D-PROV-1.C RED evidence is the missing / invalid / mismatch cases
    plus their no-publication assertions. Because a value-equality assertion
    cannot distinguish "published from the measured record" from "published from
    the probe", Task 7 carries an explicit code-review item for that distinction;
    no brittle source-string test is invented to manufacture RED here.
    """
    source = _byte_bound_source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _byte_bound_refinement(probe)
    result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured, use_real_refinement=True)
    payload = result.bundle.payload
    assert payload["source"]["timebase"] == {"num": 1, "den": 1000}
    assert payload["refinement"]["timebase"] == {"num": 1, "den": 1000}
    assert (tmp_path / "out" / "review-bundle.json").exists()
    assert result.bundle.payload["refinement"]["status"] == "MEASURED"


# --------------------------------------------------------------------------
# D5 (owner decision) — the authoritative measured time_base shape is exact.
# D6 — the service must never upgrade an authoritative evidence class.
# D7 — guard: exact endpoint selection must not depend on the diagnostic helper.
# --------------------------------------------------------------------------

def test_measured_timebase_with_extra_keys_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    """D5: an extra-key time_base must fail closed, not be normalized away.

    Accepting the extra key would publish a compact num/den that real_plan's
    exact-mapping comparison can still satisfy, so the inconsistency would only
    surface much later as an unplannable sealed bundle.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000, "display_rate": "25"})
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_authoritative_weaker_evidence_class_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    """D6-A: the adapter's binding_eligible wrapper flag must never upgrade a class."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["evidence_class"] = "EDITORIAL_INFERENCE"
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_CLASS_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_authoritative_missing_evidence_class_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    """D6-B: an absent class must refuse rather than default to MEASURED."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    del measured["evidence_class"]
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_CLASS_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


@pytest.mark.parametrize("other_class", ["MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED", "measured", ""])
def test_authoritative_other_evidence_classes_refuse(tmp_path: Path, monkeypatch, other_class) -> None:
    """D6: no case-variant or sibling class may be broadened into MEASURED."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["evidence_class"] = other_class
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_CLASS_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


def test_measured_evidence_class_positive_guard(tmp_path: Path, monkeypatch) -> None:
    """D6-C: POSITIVE_GUARD — a validated MEASURED record still publishes and
    the compact refinement sources its class from the authoritative record."""
    source = _byte_bound_source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _byte_bound_refinement(probe)
    result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    payload = result.bundle.payload
    assert payload["refinement"]["evidence_class"] == measured["evidence_class"]
    assert payload["refinement"]["evidence_class"] == "MEASURED"
    assert payload["refinement"]["status"] == "MEASURED"
    assert (tmp_path / "out" / "review-bundle.json").exists()


def test_endpoint_selection_does_not_call_the_diagnostic_observed_pts(tmp_path: Path, monkeypatch) -> None:
    """D7 GUARD: exact endpoints must not depend on the diagnostic inventory.

    `_observed_pts` is retained for diagnostics only; if endpoint selection ever
    reached it again, packet PTS could re-enter exact authority.
    """
    import vip_fvs.real_source_service as service

    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(120,))
    monkeypatch.setattr(
        service, "_observed_pts",
        lambda *a, **k: pytest.fail("endpoint selection consulted the diagnostic _observed_pts"),
    )
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


# --------------------------------------------------------------------------
# Independent-review hardening of the D5/D6 boundary.
# A Mapping may lie about keys() and a str subclass may lie about __eq__, so
# both predicates are pinned to exact structural checks; and all authoritative
# reads must complete before any artifact is written.
# --------------------------------------------------------------------------

class _TwoKeyMapping(dict):
    """A Mapping that claims only num/den while carrying an extra key."""

    def keys(self):
        return ["num", "den"]


class _EqualLiar(str):
    """A str subclass that claims equality with anything."""

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return False

    __hash__ = str.__hash__


def test_timebase_mapping_lying_about_keys_refuses(tmp_path: Path, monkeypatch) -> None:
    """D5: key-set validation must iterate the mapping, not trust keys()."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base=_TwoKeyMapping({"num": 1, "den": 1000, "display_rate": "25"}))
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_evidence_class_str_subclass_lying_about_equality_refuses(tmp_path: Path, monkeypatch) -> None:
    """D6: the class predicate must be exact-type, not __eq__-based."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["evidence_class"] = _EqualLiar("EDITORIAL_INFERENCE")
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_CLASS_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_missing_evidence_digest_refuses_before_any_artifact_write(tmp_path: Path, monkeypatch) -> None:
    """D-B: required authoritative reads must complete before the artifact write.

    Otherwise a raw KeyError escapes after a partial artifact write, so
    refusal-catching callers see neither a bundle nor a RealSourcePreparationRefusal.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    del measured["evidence_digest"]
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


@pytest.mark.parametrize("bad_id", ["../escaped", "../../pwned", "a/b", "", None, 7, "with space"])
def test_unsafe_refinement_id_refuses_without_publishing(tmp_path: Path, monkeypatch, bad_id) -> None:
    """D-C: refinement_id is a path component and must be a safe filename.

    An unvalidated value can write an artifact outside output_root before the
    bundle is ever validated.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["refinement_id"] = bad_id
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))
    # nothing may escape output_root
    assert not (tmp_path / "escaped.json").exists()
    assert not (tmp_path / "pwned.json").exists()


# --------------------------------------------------------------------------
# Second independent review: hostile Mapping variants and a post-write bound.
# The durable rule is that the authoritative time_base is normalized to a plain
# dict and the artifact bytes are serialized BEFORE any write.
# --------------------------------------------------------------------------

class _IterLiarMapping(dict):
    """Claims to contain only num/den while actually storing an extra key.

    NOTE: ``dict(measured)`` legitimately sees the real stored entries, so this
    variant is caught by the exact-key-set check on the *normalized* dict.
    """

    def __iter__(self):
        return iter(("num", "den"))

    def keys(self):
        return ["num", "den"]

    def items(self):
        return [(k, self[k]) for k in ("num", "den")]


class _GetLiarMapping(dict):
    """Stores one timebase but answers .get() with a different, projectable one.

    NOTE: normalization reads the real stored ``num``/``den``, so the lie cannot
    reach the bundle; the honest values then fail the probe-tuple comparison.
    """

    def get(self, key, default=None):
        if key in ("num", "den"):
            return 1 if key == "num" else 1000
        return default


class _NonSerializableMapping(Mapping):
    """A Mapping whose values cannot be serialized to JSON."""

    def __init__(self, store):
        self._store = store

    def __getitem__(self, key):
        return self._store[key]

    def __iter__(self):
        return iter(("num", "den"))

    def __len__(self):
        return 2


def test_iter_lying_timebase_mapping_cannot_persist_a_divergent_timebase(tmp_path: Path, monkeypatch) -> None:
    """D5: a Mapping may hide entries behind __iter__/keys/items.

    Normalization alone cannot enumerate a deliberately hidden key, so the
    durable invariant is that the PERSISTED record carries the validated plain
    timebase: the artifact and the bundle can never disagree, and no extension
    can survive into the sealed artifact.
    """
    source = _byte_bound_source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _byte_bound_refinement(probe)
    measured["time_base"] = _IterLiarMapping({"num": 1, "den": 1000, "display_rate": "25"})
    measured["evidence_digest"] = _honest_digest(measured)
    result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    artifact = json.loads(pathlib.Path(result.bundle.payload["refinement"]["evidence_artifact_ref"]).read_bytes())
    assert artifact["time_base"] == {"num": 1, "den": 1000}
    assert "display_rate" not in artifact["time_base"]
    assert artifact["time_base"] == result.bundle.payload["refinement"]["timebase"]
    assert artifact["source_probe_artifact_ref"] == probe.canonical_probe_artifact_ref
    assert artifact["source_probe_digest"] == probe.probe_digest


def test_get_lying_timebase_mapping_refuses_instead_of_contradicting_the_artifact(tmp_path: Path, monkeypatch) -> None:
    """D5: validation must read the same normalized values that get serialized.

    Otherwise the bundle could carry one timebase while the persisted artifact
    carries another.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base=_GetLiarMapping({"num": 5, "den": 7}))
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_unserializable_authoritative_mapping_refuses_before_any_write(tmp_path: Path, monkeypatch) -> None:
    """B: a hostile Mapping must refuse, not escape as a raw serialization error."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["method"] = _NonSerializableMapping({"num": 1, "den": 2})
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_NOT_SERIALIZABLE"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_timebase_values_are_persisted_exactly_as_validated(tmp_path: Path, monkeypatch) -> None:
    """D5 positive guard: the artifact and bundle must agree on the timebase."""
    source = _byte_bound_source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _byte_bound_refinement(probe)
    result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    artifact = json.loads(pathlib.Path(result.bundle.payload["refinement"]["evidence_artifact_ref"]).read_bytes())
    assert artifact["time_base"] == {"num": 1, "den": 1000}
    assert result.bundle.payload["refinement"]["timebase"] == {"num": 1, "den": 1000}
    assert artifact["time_base"] == result.bundle.payload["refinement"]["timebase"]


def test_artifact_reference_length_refuses_before_the_write(tmp_path: Path, monkeypatch) -> None:
    """A: the evidence_artifact_ref bound must be checked before writing.

    A deep output_root plus a gate-accepted id can exceed ReviewBundle's 256-char
    bound, which would otherwise leave an artifact on disk and escape as a raw
    ValueError after the write.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    deep = tmp_path / ("d" * 120) / ("e" * 120)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_ARTIFACT_REF_TOO_LONG"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured, output_root=deep)
    assert not (deep / "review-bundle.json").exists()
    assert not list((deep / "refinement").glob("*.json"))


@pytest.mark.parametrize("field,liar", [
    ("source_revision_id", "WRONG-REV"),
    ("source_content_digest", "0" * 64),
])
def test_scope_and_digest_fields_cannot_be_forged_by_equality_liars(tmp_path: Path, monkeypatch, field, liar) -> None:
    """D: the scope/digest predicates must not be defeatable by __eq__ liars."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured[field] = _EqualLiar(liar) if field == "source_revision_id" else _EqualLiar(liar)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


# --------------------------------------------------------------------------
# Final owner-authorized closure: the persisted authoritative refinement must
# still satisfy Gate-3's evidence projection, because the service normalizes an
# evidence-bearing field (time_base) before persisting.
# --------------------------------------------------------------------------

class _VisibleOnlyMapping(dict):
    """A time_base whose serialized view differs from what is stored.

    ``_IterLiarMapping`` is caught by the exact-key-set check; this variant keeps
    a BENIGN visible ``num``/``den`` so it passes every earlier predicate, while
    serializing (and therefore digesting) a materially different projection.  It
    is the case that binds the producer digest to the persisted projection.
    """

    def __iter__(self):
        return iter(("num", "den"))

    def keys(self):
        return ["num", "den"]

    def items(self):
        return [(k, self[k]) for k in ("num", "den")]


def _honest_digest(record: dict) -> str:
    return _gate3_authority.evidence_digest(_gate3_authority.RECORD_KIND_REFINEMENT, record)


def test_forged_evidence_digest_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    """Test A: a forged 64-hex digest must not be published."""
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["evidence_digest"] = "0" * 64
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_DIGEST_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_invalid_evidence_digest_shape_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    """Test B: a non-64-hex digest must fail closed before publication.

    Pre-change this is a GUARD: the existing missing-digest predicate already
    refuses a non-string/empty value, but a well-formed-but-invalid *string* of
    the wrong shape previously reached publication.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["evidence_digest"] = "not-a-digest"
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_DIGEST_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_digest_is_verified_over_the_normalized_projection_before_any_write(tmp_path: Path, monkeypatch) -> None:
    """Test C: the digest is verified against the NORMALIZED persisted projection.

    Two facts are pinned here, both reachable in the shipped code:

    1. the projection the service persists is the same projection the digest is
       verified against — adding the two source-probe fields does not move the
       digest, because they are not evidence-bearing; and
    2. a digest that does not match the record the service actually holds is
       refused before any write, never recomputed and silently replaced.

    A Mapping whose visible view hides entries cannot be used to force a
    normalization-only divergence, because the exact-key-set predicate refuses
    any time_base carrying an extra entry before the digest is consulted; and a
    diverging numeric time_base is refused by the probe-tuple comparison, which
    is likewise upstream of the digest check.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})

    persisted_shape = dict(measured)
    persisted_shape["time_base"] = {"num": 1, "den": 1000}
    persisted_shape["source_probe_artifact_ref"] = probe.canonical_probe_artifact_ref
    persisted_shape["source_probe_digest"] = probe.probe_digest
    # The probe fields are not evidence-bearing, so the digest is unchanged by
    # their presence; this is asserted against the producer's own value.
    assert _honest_digest(persisted_shape) == measured["evidence_digest"]

    forged = dict(measured)
    forged["evidence_digest"] = "1" * 64
    assert forged["evidence_digest"] != _honest_digest(forged)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_DIGEST_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=forged)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_published_artifact_satisfies_gate3_evidence_digest(tmp_path: Path, monkeypatch) -> None:
    """Test D/E: POSITIVE_GUARD proving the emitted artifact is plan-loadable.

    This is the mechanical guarantee that a service-published artifact will not
    later fail real_plan's `_load_authoritative_refinement`.
    """
    source = _byte_bound_source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _byte_bound_refinement(probe)
    result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)

    artifact_path = pathlib.Path(result.bundle.payload["refinement"]["evidence_artifact_ref"])
    artifact = json.loads(artifact_path.read_bytes())
    checked = _gate3_authority.assert_evidence_digest(_gate3_authority.RECORD_KIND_REFINEMENT, artifact)
    assert isinstance(checked, str)
    assert checked == artifact["evidence_digest"]
    assert checked == result.bundle.payload["refinement"]["evidence_digest"]
    assert artifact["time_base"] == result.bundle.payload["refinement"]["timebase"]


_TRUE_DIGEST_SENTINEL = "<the-record's-own-true-digest>"


@pytest.mark.parametrize("digest_value", [
    _TRUE_DIGEST_SENTINEL, "d" * 64, "0" * 64, "not-a-digest", "D" * 64, "a" * 63, "a" * 65,
])
def test_digest_values_are_never_silently_replaced(tmp_path: Path, monkeypatch, digest_value) -> None:
    """The service must refuse a disagreeing digest, never rewrite it to match.

    A digest that already equals its projection publishes unchanged; every other
    value refuses rather than being replaced by a recomputed one.
    """
    source = _byte_bound_source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = (_byte_bound_refinement(probe) if digest_value == _TRUE_DIGEST_SENTINEL
                else _measured_base(source, time_base={"num": 1, "den": 1000}))
    true_digest = measured["evidence_digest"]
    measured["evidence_digest"] = true_digest if digest_value == _TRUE_DIGEST_SENTINEL else digest_value
    if digest_value == _TRUE_DIGEST_SENTINEL:
        result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
        artifact = json.loads(pathlib.Path(result.bundle.payload["refinement"]["evidence_artifact_ref"]).read_bytes())
        # The persisted projection also carries the two probe fields the service
        # injects; they are not evidence-bearing, so recomputing over them must
        # reproduce the emitted digest exactly.
        expected = dict(measured)
        expected["source_probe_artifact_ref"] = artifact["source_probe_artifact_ref"]
        expected["source_probe_digest"] = artifact["source_probe_digest"]
        assert artifact["evidence_digest"] == _honest_digest(expected)
    else:
        with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_EVIDENCE_DIGEST_MISMATCH"):
            _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
        assert not (tmp_path / "out" / "review-bundle.json").exists()
        assert not list((tmp_path / "out" / "refinement").glob("*.json"))


def test_unserializable_evidence_projection_refuses_with_the_named_code(tmp_path: Path, monkeypatch) -> None:
    """The digest revalidation must not escape as a raw serialization error.

    `assert_evidence_digest` canonicalizes the evidence projection, so a
    projected field holding a non-finite float or a non-dict Mapping raises from
    the encoder.  That must surface as a RealSourcePreparationRefusal (the module
    contract) rather than a raw ValueError/TypeError/UnicodeEncodeError, and it
    must still happen before any write.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured["precision"] = float("nan")
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))


@pytest.mark.parametrize("field,value", [
    ("precision", _NonSerializableMapping({"num": 1, "den": 2})),
    ("frame_ordinal_basis", _NonSerializableMapping({"num": 1, "den": 2})),
    ("time_domain", "\ud800"),
])
def test_unserializable_projected_fields_refuse_with_the_named_code(tmp_path: Path, monkeypatch, field, value) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    measured[field] = value
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()
    assert not list((tmp_path / "out" / "refinement").glob("*.json"))
