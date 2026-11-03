"""Additive schema-v2 snapshot temporal evidence (Owner-approved bounded A′-7).

Authority
---------
``docs/decisions/2026-10-25-g3-a3-aprime7-bounded-owner-decision.md`` D-1..D-3 and
``docs/superpowers/plans/2026-10-25-g3-a3-aprime7-snapshot-v2-implementation.md``.

The v2 payload preserves the frozen 13-field v1 body and seals exactly seven
additional measured container facts (20 body fields + ``evidence_sha256``)::

    duration_ts, duration_consistency, tail_duration_ticks,
    presentation_origin_ticks, stream_handler, stream_identity_derivation,
    composition_offsets

``composition_offsets`` is decode-order aligned and signed, so
``sorted(dts_ticks[i] + composition_offsets[i]) == pts_ticks`` holds exactly,
including duplicate presentation ticks.  VFR is classified from presentation PTS
deltas only; the historical decode-order predicate remains exclusive to
``bind_temporal_authority`` (schema v1).

Scope boundary: this module exercises only v2 creation and dual-version
verification.  It does not implement or assert a new reordering acceptance
policy, A-7 stream-mapping acceptance, the A-12 terminal-tail policy, a new
composition module, new ``TEMPORAL_AUTHORITY_*`` error codes, IT-8 completion,
or any v2-only consumer refusal code (PENDING A-5).

All fixtures are synthetic ISO-BMFF bytes built in-process by
``gate3.fixturegen``; no real media, network, provider, or model activity.
"""
from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import pytest

import vip_fvs.source_snapshot as source_snapshot_module
from gate3 import container as container_module
from gate3.container import parse_iso_bmff_timing_bytes
from gate3.fixturegen import build_mp4
from vip_fvs.source_snapshot import SourceSnapshotError, SourceSnapshotStore

MEDIA_TIMESCALE = 1000
UNIFORM_DELTAS = (40, 40, 40, 40)
TAIL_TICKS = 40
DURATION_TS = 160

# Case (i) from the IT-2 divergence evidence: uniform decode deltas (decode basis
# CFR) with signed composition offsets that make presentation ticks non-uniform.
REORDER_DELTAS = (40, 40, 40, 40)
REORDER_OFFSETS = (0, 80, 20, -60)

# Two samples deliberately compose onto the same presentation tick.
DUPLICATE_OFFSETS = (0, 0, -40, 0)

V1_FIELDS = {
    "schema_version", "snapshot_id", "snapshot_manifest_sha256", "source_revision_id",
    "source_sha256", "source_byte_count", "selected_stream_index", "stream_count",
    "timebase", "pts_ticks", "dts_ticks", "declared_vfr", "declared_reordering",
    "evidence_sha256",
}
V2_ADDITIONAL_FIELDS = {
    "duration_ts", "duration_consistency", "tail_duration_ticks",
    "presentation_origin_ticks", "stream_handler", "stream_identity_derivation",
    "composition_offsets",
}
V2_FIELDS = V1_FIELDS | V2_ADDITIONAL_FIELDS


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _resealed(evidence: dict) -> dict:
    """Recompute only the receipt's own ``evidence_sha256`` over a forged body."""
    body = {key: value for key, value in evidence.items() if key != "evidence_sha256"}
    forged = dict(body)
    forged["evidence_sha256"] = hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()
    return forged


def _capture(tmp_path: Path, blob: bytes, *, name: str, revision: str = "revision:synthetic-v2"):
    store = SourceSnapshotStore(
        tmp_path / name, max_source_bytes=64_000, max_store_bytes=256_000,
    )
    source = tmp_path / f"{name}-source.mp4"
    source.write_bytes(blob)
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(blob).hexdigest(),
        authorization_id=f"authorization:{name}",
        source_revision_id=revision,
    )
    return store, source, snapshot


def _bind_v1(store: SourceSnapshotStore, snapshot, *, declared_vfr: bool = False,
             declared_reordering: bool = False):
    return store.bind_temporal_authority(
        snapshot, selected_stream_index=0,
        declared_vfr=declared_vfr, declared_reordering=declared_reordering,
    )


def _bind_v2(store: SourceSnapshotStore, snapshot, *, declared_vfr: bool = False,
             declared_reordering: bool = False, stream_index: int = 0):
    return store.bind_temporal_authority_v2(
        snapshot, selected_stream_index=stream_index,
        declared_vfr=declared_vfr, declared_reordering=declared_reordering,
    )


def _patched_parse(monkeypatch: pytest.MonkeyPatch, mutate) -> None:
    """Mutate measured parser facts after a real measurement (only seam available)."""
    real_parse = container_module.parse_iso_bmff_timing_bytes

    def fake_parse(raw, *, selected_stream_index=None):
        measured = real_parse(raw, selected_stream_index=selected_stream_index)
        mutate(measured)
        return measured

    monkeypatch.setattr(container_module, "parse_iso_bmff_timing_bytes", fake_parse)


def _expected_code(call) -> str:
    with pytest.raises(SourceSnapshotError) as excinfo:
        call()
    return str(excinfo.value)


# ---------------------------------------------------------------------------
# 1. Creation contract: additive closed v2 payload, v1 untouched.
# ---------------------------------------------------------------------------


def test_v2_binding_exists_with_v1_parameter_contract(tmp_path: Path) -> None:
    """No caller-supplied temporal fact may be an input to v2 creation either."""
    store = SourceSnapshotStore(
        tmp_path / "signature-store", max_source_bytes=64_000, max_store_bytes=256_000,
    )
    parameters = inspect.signature(store.bind_temporal_authority_v2).parameters
    assert set(parameters) == {
        "snapshot", "selected_stream_index", "declared_vfr", "declared_reordering",
    }
    assert inspect.signature(store.bind_temporal_authority_v2).parameters.keys() == (
        inspect.signature(store.bind_temporal_authority).parameters.keys()
    )


def test_v2_evidence_adds_exactly_seven_closed_fields_over_v1(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="closed-fields")

    v1 = _bind_v1(store, snapshot).as_evidence()
    v2 = _bind_v2(store, snapshot).as_evidence()

    assert set(v1) == V1_FIELDS and len(v1) == 14 and v1["schema_version"] == 1
    assert set(v2) == V2_FIELDS and len(v2) == 21
    assert v2["schema_version"] == 2
    assert set(v2) - set(v1) == V2_ADDITIONAL_FIELDS
    assert set(v2) & set(v1) == V1_FIELDS
    # Facts that are not part of the approved v2 contract must not appear.
    assert "nb_frames" not in v2
    assert "has_b_frames" not in v2
    assert "pts_equals_dts" not in v2
    # The v1 and v2 receipts of the same snapshot are never interchangeable.
    assert _canonical(v1) != _canonical(v2)
    assert v1["pts_ticks"] == v2["pts_ticks"]
    assert v1["dts_ticks"] == v2["dts_ticks"]


def test_v2_evidence_seals_canonical_digest_over_the_twenty_body_fields(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="sealed-digest")
    evidence = _bind_v2(store, snapshot).as_evidence()

    body = {key: value for key, value in evidence.items() if key != "evidence_sha256"}
    assert len(body) == 20
    assert hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest() == evidence["evidence_sha256"]
    # Canonical JSON form: JSON-native lists, no tuples leaking into the receipt.
    assert isinstance(evidence["pts_ticks"], list)
    assert isinstance(evidence["composition_offsets"], list)
    assert json.loads(json.dumps(evidence)) == evidence


def test_v2_measured_facts_are_exact_for_uniform_fixture(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    facts = parse_iso_bmff_timing_bytes(blob, selected_stream_index=0)
    store, _source, snapshot = _capture(tmp_path, blob, name="exact-facts")
    evidence = _bind_v2(store, snapshot).as_evidence()

    assert evidence["duration_ts"] == facts["duration_ts"] == DURATION_TS
    assert evidence["duration_consistency"] == facts["duration_consistency"] == "MATCH"
    assert evidence["tail_duration_ticks"] == facts["tail_duration_ticks"] == TAIL_TICKS
    assert evidence["presentation_origin_ticks"] == facts["presentation_origin_ticks"] == 0
    assert evidence["stream_handler"] == facts["stream_handler"] == "vide"
    assert evidence["stream_identity_derivation"] == facts["stream_identity_derivation"]
    assert evidence["composition_offsets"] == list(facts["composition_offsets"])
    assert evidence["timebase"] == {"num": 1, "den": MEDIA_TIMESCALE}
    assert evidence["pts_ticks"] == list(facts["pts_ticks"]) == [0, 40, 80, 120]
    assert evidence["dts_ticks"] == list(facts["dts_ticks"]) == [0, 40, 80, 120]


# ---------------------------------------------------------------------------
# 2. Decode-order-aligned signed composition offsets.
# ---------------------------------------------------------------------------


def test_v2_signed_composition_offsets_are_decode_order_aligned(tmp_path: Path) -> None:
    blob = build_mp4(
        media_timescale=MEDIA_TIMESCALE,
        sample_deltas=REORDER_DELTAS,
        ctts_offsets=REORDER_OFFSETS,
    )
    facts = parse_iso_bmff_timing_bytes(blob)
    store, _source, snapshot = _capture(tmp_path, blob, name="signed-offsets")
    evidence = _bind_v2(store, snapshot, declared_vfr=True, declared_reordering=True).as_evidence()

    assert evidence["composition_offsets"] == [0, 80, 20, -60]
    assert any(offset < 0 for offset in evidence["composition_offsets"])
    assert len(evidence["composition_offsets"]) == len(evidence["dts_ticks"])
    assert evidence["dts_ticks"] == [0, 40, 80, 120]
    assert evidence["pts_ticks"] == [0, 60, 100, 120]
    # Signed composition is exact in decode order, including the negative offset.
    composed = [d + o for d, o in zip(evidence["dts_ticks"], evidence["composition_offsets"])]
    assert sorted(composed) == evidence["pts_ticks"]
    assert composed != evidence["pts_ticks"]
    # The seven sealed facts are the measured parser facts, not a re-derivation.
    assert evidence["composition_offsets"] == list(facts["composition_offsets"])
    assert evidence["presentation_origin_ticks"] == facts["presentation_origin_ticks"] == 0


def test_v2_duplicate_presentation_ticks_are_preserved_in_order(tmp_path: Path) -> None:
    """Composition may map two samples onto one presentation tick; no dedupe is legal."""
    blob = build_mp4(
        media_timescale=MEDIA_TIMESCALE,
        sample_deltas=UNIFORM_DELTAS,
        ctts_offsets=DUPLICATE_OFFSETS,
    )
    facts = parse_iso_bmff_timing_bytes(blob)
    assert facts["pts_ticks"] == (0, 40, 40, 120)
    assert facts["composition_offsets"] == (0, 0, -40, 0)

    store, _source, snapshot = _capture(tmp_path, blob, name="duplicate-pts")
    evidence = _bind_v2(store, snapshot, declared_vfr=True, declared_reordering=True).as_evidence()

    assert evidence["pts_ticks"] == [0, 40, 40, 120]
    assert len(evidence["pts_ticks"]) == 4
    assert evidence["pts_ticks"].count(40) == 2
    composed = [d + o for d, o in zip(evidence["dts_ticks"], evidence["composition_offsets"])]
    assert sorted(composed) == evidence["pts_ticks"]


def test_v2_refuses_nonzero_presentation_origin_without_normalizing(tmp_path: Path) -> None:
    """A-9 strict-V1 origin-zero still holds for v2; the origin is never subtracted."""
    blob = build_mp4(
        media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS, media_time_offset=100,
    )
    assert parse_iso_bmff_timing_bytes(blob)["presentation_origin_ticks"] == 100
    store, _source, snapshot = _capture(tmp_path, blob, name="nonzero-origin")

    assert _expected_code(lambda: _bind_v2(store, snapshot)) == "EDIT_LIST_ORIGIN_NOT_APPLIED"
    assert _expected_code(lambda: _bind_v1(store, snapshot)) == "EDIT_LIST_ORIGIN_NOT_APPLIED"


# ---------------------------------------------------------------------------
# 3. A-12 tail/duration boundary: v2 seals MISMATCH, it does not auto-refuse.
# ---------------------------------------------------------------------------


def test_v2_binds_duration_mismatch_and_seals_the_mismatch(tmp_path: Path) -> None:
    """A-12 remains PENDING: v2 records the disagreement rather than deciding it."""
    blob = build_mp4(
        media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS, declared_duration=999,
    )
    facts = parse_iso_bmff_timing_bytes(blob)
    assert facts["duration_ts"] == 999
    assert facts["pts_ticks"][-1] + facts["tail_duration_ticks"] == DURATION_TS
    assert facts["duration_consistency"] == "MISMATCH"

    store, _source, snapshot = _capture(tmp_path, blob, name="duration-mismatch-v2")
    evidence = _bind_v2(store, snapshot).as_evidence()

    assert evidence["duration_ts"] == 999
    assert evidence["duration_consistency"] == "MISMATCH"
    # The receipt still replays against the retained bytes; the policy is not invented.
    rebound = store.verify_temporal_authority(snapshot, json.loads(json.dumps(evidence)))
    assert rebound.as_evidence() == evidence


# ---------------------------------------------------------------------------
# 4. Negative controls: fabricated or ill-typed measured facts never bind.
# ---------------------------------------------------------------------------


def _measure_and_bind(store: SourceSnapshotStore, snapshot, mutate) -> None:
    """Bind under a temporary parser-fact mutation and restore the parser after."""
    original = container_module.parse_iso_bmff_timing_bytes

    def fake_parse(raw, *, selected_stream_index=None):
        measured = original(raw, selected_stream_index=selected_stream_index)
        mutate(measured)
        return measured

    container_module.parse_iso_bmff_timing_bytes = fake_parse
    try:
        _bind_v2(store, snapshot)
    finally:
        container_module.parse_iso_bmff_timing_bytes = original


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("duration-ts-absent", lambda m: m.pop("duration_ts")),
        ("duration-ts-string", lambda m: m.__setitem__("duration_ts", "160")),
        ("duration-ts-bool", lambda m: m.__setitem__("duration_ts", True)),
        ("duration-ts-negative", lambda m: m.__setitem__("duration_ts", -1)),
        ("consistency-lowercase", lambda m: m.__setitem__("duration_consistency", "match")),
        ("consistency-unknown", lambda m: m.__setitem__("duration_consistency", "PARTIAL")),
        ("consistency-fabricated", lambda m: m.__setitem__("duration_consistency", "MISMATCH")),
        ("consistency-not-string", lambda m: m.__setitem__("duration_consistency", 1)),
        ("tail-absent", lambda m: m.pop("tail_duration_ticks")),
        ("tail-zero", lambda m: m.__setitem__("tail_duration_ticks", 0)),
        ("tail-negative", lambda m: m.__setitem__("tail_duration_ticks", -40)),
        ("tail-bool", lambda m: m.__setitem__("tail_duration_ticks", True)),
        ("origin-absent", lambda m: m.pop("presentation_origin_ticks")),
        ("origin-string", lambda m: m.__setitem__("presentation_origin_ticks", "0")),
        ("handler-non-video", lambda m: m.__setitem__("stream_handler", "soun")),
        ("handler-absent", lambda m: m.pop("stream_handler")),
        ("handler-not-string", lambda m: m.__setitem__("stream_handler", b"vide")),
        ("derivation-absent", lambda m: m.pop("stream_identity_derivation")),
        ("derivation-empty", lambda m: m.__setitem__("stream_identity_derivation", "   ")),
        ("derivation-not-string", lambda m: m.__setitem__("stream_identity_derivation", 1)),
        ("offsets-absent", lambda m: m.pop("composition_offsets")),
        ("offsets-wrong-length", lambda m: m.__setitem__("composition_offsets", (0, 0, 0))),
        ("offsets-not-tuple", lambda m: m.__setitem__("composition_offsets", [0, 0, 0, 0])),
        ("offsets-bool-element", lambda m: m.__setitem__("composition_offsets", (0, True, 0, 0))),
        ("offsets-fabricated", lambda m: m.__setitem__("composition_offsets", (0, 40, 0, 0))),
        ("offsets-disagree-with-pts", lambda m: m.__setitem__("composition_offsets", (0, 0, 0, 80))),
    ],
)
def test_v2_refuses_fabricated_or_ill_typed_measured_fact(
    tmp_path: Path, label: str, mutate,
) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name=f"fact-{label}")
    assert _expected_code(lambda: _measure_and_bind(store, snapshot, mutate)) == (
        "SNAPSHOT_TEMPORAL_FACTS_INVALID"
    )


def test_v2_refuses_measured_stream_index_disagreement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="stream-disagreement-v2")
    _patched_parse(monkeypatch, lambda measured: measured.__setitem__("stream_index", 1))

    assert _expected_code(lambda: _bind_v2(store, snapshot)) == "SNAPSHOT_TEMPORAL_STREAM_MISMATCH"


def test_v2_refuses_measured_byte_digest_disagreement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="digest-disagreement-v2")
    _patched_parse(monkeypatch, lambda measured: measured.__setitem__("source_bytes_sha256", "0" * 64))

    assert _expected_code(lambda: _bind_v2(store, snapshot)) == "SNAPSHOT_TEMPORAL_DIGEST_MISMATCH"


def test_v2_post_measurement_snapshot_mutation_is_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The retained bytes are re-verified after measuring, before sealing."""
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="post-measurement-tamper")
    real_parse = container_module.parse_iso_bmff_timing_bytes

    def fake_parse(raw, *, selected_stream_index=None):
        measured = real_parse(raw, selected_stream_index=selected_stream_index)
        path = snapshot.snapshot_path
        path.chmod(0o600)
        current = path.read_bytes()
        path.write_bytes(current[:-1] + bytes([current[-1] ^ 0xFF]))
        path.chmod(0o400)
        return measured

    monkeypatch.setattr(container_module, "parse_iso_bmff_timing_bytes", fake_parse)

    assert _expected_code(lambda: _bind_v2(store, snapshot)) == "SNAPSHOT_DIGEST_MISMATCH"


# ---------------------------------------------------------------------------
# 5. Presentation-basis VFR classification (IT-2 correction, v2 only).
# ---------------------------------------------------------------------------


def test_v2_classifies_vfr_from_presentation_deltas_only(tmp_path: Path) -> None:
    """Decode order says CFR; measured presentation spacing says VFR."""
    blob = build_mp4(
        media_timescale=MEDIA_TIMESCALE,
        sample_deltas=REORDER_DELTAS,
        ctts_offsets=REORDER_OFFSETS,
    )
    store, _source, snapshot = _capture(tmp_path, blob, name="presentation-vfr")

    # Legacy v1 keeps its historical decode-order predicate: CFR binds, VFR refuses.
    assert _bind_v1(store, snapshot, declared_vfr=False, declared_reordering=True).declared_vfr is False
    assert _expected_code(
        lambda: _bind_v1(store, snapshot, declared_vfr=True, declared_reordering=True)
    ) == "SNAPSHOT_VFR_DECLARATION_MISMATCH"

    # v2 refuses the declaration that only agrees with decode order ...
    assert _expected_code(
        lambda: _bind_v2(store, snapshot, declared_vfr=False, declared_reordering=True)
    ) == "SNAPSHOT_VFR_DECLARATION_MISMATCH"
    # ... and binds the presentation-basis declaration.
    binding = _bind_v2(store, snapshot, declared_vfr=True, declared_reordering=True)
    assert binding.declared_vfr is True
    assert binding.pts_ticks == (0, 60, 100, 120)


def test_v2_classifies_cfr_from_presentation_deltas_only(tmp_path: Path) -> None:
    """Decode order says VFR; measured presentation spacing says CFR."""
    deltas = (30, 50, 40, 40)
    offsets = (0, 50, -40, 0)
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=deltas, ctts_offsets=offsets)
    facts = parse_iso_bmff_timing_bytes(blob)
    assert facts["dts_ticks"] == (0, 30, 80, 120)
    assert facts["pts_ticks"] == (0, 40, 80, 120)
    store, _source, snapshot = _capture(tmp_path, blob, name="presentation-cfr")

    # Legacy v1: decode order is VFR, so the CFR declaration is refused there.
    assert _expected_code(
        lambda: _bind_v1(store, snapshot, declared_vfr=False, declared_reordering=True)
    ) == "SNAPSHOT_VFR_DECLARATION_MISMATCH"

    assert _expected_code(
        lambda: _bind_v2(store, snapshot, declared_vfr=True, declared_reordering=True)
    ) == "SNAPSHOT_VFR_DECLARATION_MISMATCH"
    binding = _bind_v2(store, snapshot, declared_vfr=False, declared_reordering=True)
    assert binding.declared_vfr is False
    assert binding.pts_ticks == (0, 40, 80, 120)


# ---------------------------------------------------------------------------
# 6. Dual-version verification, closed field sets, version pinning.
# ---------------------------------------------------------------------------


def test_v2_evidence_replays_after_json_round_trip(tmp_path: Path) -> None:
    blob = build_mp4(
        media_timescale=MEDIA_TIMESCALE,
        sample_deltas=REORDER_DELTAS,
        ctts_offsets=REORDER_OFFSETS,
    )
    store, _source, snapshot = _capture(tmp_path, blob, name="round-trip-v2")
    evidence = _bind_v2(store, snapshot, declared_vfr=True, declared_reordering=True).as_evidence()

    reloaded = json.loads(json.dumps(evidence))
    assert reloaded == evidence
    binding = store.verify_temporal_authority(snapshot, reloaded)
    assert binding.as_evidence() == evidence
    assert binding.composition_offsets == (0, 80, 20, -60)


def test_v1_receipt_still_verifies_alongside_v2(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="both-versions")
    v1_evidence = _bind_v1(store, snapshot).as_evidence()
    v2_evidence = _bind_v2(store, snapshot).as_evidence()

    v1_binding = store.verify_temporal_authority(snapshot, v1_evidence)
    v2_binding = store.verify_temporal_authority(snapshot, v2_evidence)
    assert v1_binding.as_evidence() == v1_evidence
    assert v2_binding.as_evidence() == v2_evidence
    assert v1_binding.as_evidence()["schema_version"] == 1
    assert v2_binding.as_evidence()["schema_version"] == 2


def test_relabelled_v1_receipt_refuses_as_binding_mismatch(tmp_path: Path) -> None:
    """A v1 receipt that only changed ``schema_version`` to 2 is not v2 evidence."""
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="relabelled-v1")
    relabelled = dict(_bind_v1(store, snapshot).as_evidence())
    relabelled["schema_version"] = 2
    assert set(relabelled) == V1_FIELDS

    assert _expected_code(
        lambda: store.verify_temporal_authority(snapshot, relabelled)
    ) == "SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"


@pytest.mark.parametrize(
    "label",
    ["mixed", "removed", "extra", "v2-as-v1"],
)
def test_non_closed_v2_payload_refuses_the_field_layer(tmp_path: Path, label: str) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name=f"closed-{label}")
    evidence = _bind_v2(store, snapshot).as_evidence()

    forged = dict(evidence)
    if label == "mixed":
        forged.pop("composition_offsets")
        forged["declared_vfr"] = evidence["declared_vfr"]
        forged["unexpected_field"] = 1
    elif label == "removed":
        forged.pop("stream_handler")
    elif label == "extra":
        forged["nb_frames"] = 4
    else:
        forged["schema_version"] = 1

    assert _expected_code(
        lambda: store.verify_temporal_authority(snapshot, forged)
    ) == "SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID"


def test_v2_evidence_type_layer_refuses_noncanonical_encoding(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="v2-tuple-encoding")
    forged = dict(_bind_v2(store, snapshot).as_evidence())
    forged["pts_ticks"] = tuple(forged["pts_ticks"])
    forged["dts_ticks"] = tuple(forged["dts_ticks"])
    forged["composition_offsets"] = tuple(forged["composition_offsets"])

    assert _expected_code(
        lambda: store.verify_temporal_authority(snapshot, forged)
    ) == "SNAPSHOT_TEMPORAL_EVIDENCE_TYPES_INVALID"


@pytest.mark.parametrize(
    "field",
    [
        "pts_ticks", "dts_ticks", "composition_offsets", "duration_ts",
        "tail_duration_ticks", "timebase", "source_revision_id", "snapshot_id",
    ],
)
def test_tampered_and_resealed_v2_fact_refuses_binding_mismatch(
    tmp_path: Path, field: str,
) -> None:
    """A self-consistent forgery is still refused against the retained bytes."""
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name=f"resealed-{field}")
    evidence = _bind_v2(store, snapshot).as_evidence()

    forged = json.loads(json.dumps(evidence))
    if field == "timebase":
        forged["timebase"] = {"num": 1, "den": 900}
    elif field == "duration_ts":
        forged["duration_ts"] = 999
        forged["duration_consistency"] = "MATCH"
    elif isinstance(forged[field], list):
        forged[field][0] = forged[field][0] + 11
    else:
        forged[field] = 7 if isinstance(forged[field], int) else "rev:forged"
    forged = _resealed(forged)
    assert _canonical(forged) != _canonical(evidence)

    assert _expected_code(
        lambda: store.verify_temporal_authority(snapshot, forged)
    ) == "SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"


def test_wrong_v2_evidence_digest_refuses_binding_mismatch(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="v2-bad-digest")
    evidence = _bind_v2(store, snapshot).as_evidence()
    original = evidence["evidence_sha256"]
    forged = dict(evidence)
    forged["evidence_sha256"] = ("e" if original[0] != "e" else "f") + original[1:]

    assert _expected_code(
        lambda: store.verify_temporal_authority(snapshot, forged)
    ) == "SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"


def test_tampered_retained_bytes_refuse_v2_verification(tmp_path: Path) -> None:
    blob = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)
    store, _source, snapshot = _capture(tmp_path, blob, name="v2-tampered-bytes")
    evidence = _bind_v2(store, snapshot).as_evidence()

    path = snapshot.snapshot_path
    path.chmod(0o600)
    path.write_bytes(path.read_bytes()[:-10])
    path.chmod(0o400)

    assert _expected_code(
        lambda: store.verify_temporal_authority(snapshot, evidence)
    ) == "SNAPSHOT_DIGEST_MISMATCH"


# ---------------------------------------------------------------------------
# 7. Approved scope boundary: no invented error-code namespace.
# ---------------------------------------------------------------------------


def test_v2_adds_no_temporal_authority_error_code_namespace() -> None:
    source = inspect.getsource(source_snapshot_module)
    assert "TEMPORAL_AUTHORITY_" not in source
