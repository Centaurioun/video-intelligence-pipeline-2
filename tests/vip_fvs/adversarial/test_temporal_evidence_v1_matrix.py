"""Authorized-v1 gaps in the 12-case temporal-evidence test matrix.

Scope
-----
This module fills only the genuinely authorized ``schema_version == 1`` gaps left
by the existing temporal-evidence suite.  The case numbering follows the
12-case requirement recorded in
``docs/agent-runs/2026-10-25-g3-temporal-binding-wave3/v1-coverage-matrix.md``.

Cases 1, 3 (partly), 4 (partly), 6, 7, 8 and 9 are already covered by
``tests/vip_fvs/unit/test_source_snapshot_temporal_origin_refusal.py``,
``tests/vip_fvs/adversarial/test_source_snapshot_temporal_safety.py``,
``tests/vip_fvs/adversarial/test_temporal_vfr_basis_divergence.py`` and
``tests/vip_fvs/integration/test_source_snapshot_temporal_authority_successor.py``.
The tests below add the measured evidence for cases 3, 4, 5, 10, 11 and 12.

Case 2 (valid v2 evidence) is **BLOCKED** pending authority A-3 and MUST NOT gain
a test here: no v2 evidence schema has been authorized, so a v2 test would encode
an invented contract.

Every fixture is synthetic bytes built in-process by ``gate3.fixturegen`` and
captured through ``SourceSnapshotStore`` under ``tmp_path``; no real media,
network, provider, model or ffmpeg dependency is involved.  Refusal codes below
are *measured* on this branch before this module was committed (working-tree run in
``.worktrees/g3-temporal-binding-wave3``), not guessed.

Case 10 is the load-bearing defect capture.  The parser emits
``duration_consistency == "MISMATCH"`` when ``mdhd`` duration disagrees with
``presentation[-1] + tail``, but ``bind_temporal_authority`` never reads that
fact, so a duration-inconsistent source still binds and still issues
``schema_version: 1`` evidence.  The tail/duration policy is PENDING (A-12/IT-6);
the corrected expectation is recorded as a strict ``xfail`` tripwire and the
current (defective) behaviour is pinned by a passing test so the defect cannot
be blurred.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from gate3 import container as container_module
from gate3.container import parse_iso_bmff_timing_bytes
from gate3.fixturegen import build_mp4, build_multi_trak_mp4
from vip_fvs.source_snapshot import SourceSnapshotError, SourceSnapshotStore

MEDIA_TIMESCALE = 1000
UNIFORM_DELTAS = (40, 40, 40, 40)

# Uniform decode deltas with no composition offsets -> declared_vfr=False,
# declared_reordering=False.
CFR_BYTES = build_mp4(media_timescale=MEDIA_TIMESCALE, sample_deltas=UNIFORM_DELTAS)

# ``mdhd`` duration deliberately disagrees with presentation[-1] + tail.
DURATION_INCONSISTENT_BYTES = build_mp4(
    media_timescale=MEDIA_TIMESCALE,
    sample_deltas=UNIFORM_DELTAS,
    declared_duration=999,
)

_V1_EVIDENCE_FIELDS = {
    "schema_version", "snapshot_id", "snapshot_manifest_sha256", "source_revision_id",
    "source_sha256", "source_byte_count", "selected_stream_index", "stream_count",
    "timebase", "pts_ticks", "dts_ticks", "declared_vfr", "declared_reordering",
    "evidence_sha256",
}


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _store(tmp_path: Path, name: str) -> SourceSnapshotStore:
    return SourceSnapshotStore(
        tmp_path / name, max_source_bytes=64_000, max_store_bytes=256_000,
    )


def _capture(tmp_path: Path, blob: bytes, *, name: str, revision: str = "revision:synthetic"):
    store = _store(tmp_path, name)
    source = tmp_path / f"{name}-source.mp4"
    source.write_bytes(blob)
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(blob).hexdigest(),
        authorization_id="authorization:synthetic",
        source_revision_id=revision,
    )
    return store, source, snapshot


def _bind(store: SourceSnapshotStore, snapshot, *, stream_index: int = 0):
    return store.bind_temporal_authority(
        snapshot,
        selected_stream_index=stream_index,
        declared_vfr=False,
        declared_reordering=False,
    )


def _private_rewrite(path: Path, data: bytes) -> None:
    """Rewrite a ``0o400`` retained evidence file without tripping the permission gate."""
    path.chmod(0o600)
    path.write_bytes(data)
    path.chmod(0o400)


def _forge_manifest(snapshot) -> None:
    """Tamper the on-disk manifest while recomputing only its internal self-digest.

    ``snapshot.manifest_sha256`` (the value held by the caller/evidence) is left
    stale, which models an on-disk tamper rather than a consistent re-capture.
    """
    manifest = json.loads(snapshot.manifest_path.read_text())
    manifest["threat_model"] = "tampered_after_capture"
    body = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    _private_rewrite(snapshot.manifest_path, json.dumps(manifest).encode())


def _patched_parse(monkeypatch: pytest.MonkeyPatch, mutate) -> None:
    """Apply ``mutate`` to the production parser's measured facts.

    Mirrors the origin-refusal test's approach: the parser output is mutated
    *after* a real measurement, so the mutation is the only non-measured input.
    """
    real_parse = container_module.parse_iso_bmff_timing_bytes

    def fake_parse(raw, *, selected_stream_index=None):
        measured = real_parse(raw, selected_stream_index=selected_stream_index)
        mutate(measured)
        return measured

    monkeypatch.setattr(container_module, "parse_iso_bmff_timing_bytes", fake_parse)


# ---------------------------------------------------------------------------
# Case 3: tampered source bytes / manifest / evidence provenance facts.
# ---------------------------------------------------------------------------


def test_tampered_retained_source_bytes_refuse_temporal_verification(tmp_path: Path) -> None:
    """The consumer of a v1 receipt re-verifies the retained bytes, not just the digest."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="tamper-source")
    evidence = _bind(store, snapshot).as_evidence()

    truncated = snapshot.snapshot_path.read_bytes()[:-10]
    _private_rewrite(snapshot.snapshot_path, truncated)

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, evidence)
    assert str(excinfo.value) == "SNAPSHOT_DIGEST_MISMATCH"

    with pytest.raises(SourceSnapshotError) as bind_excinfo:
        _bind(store, snapshot)
    assert str(bind_excinfo.value) == "SNAPSHOT_DIGEST_MISMATCH"


def test_tampered_manifest_body_refuses_temporal_verification(tmp_path: Path) -> None:
    """An internally self-consistent but rewritten manifest is refused by the held digest."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="tamper-manifest")
    evidence = _bind(store, snapshot).as_evidence()

    _forge_manifest(snapshot)

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, evidence)
    assert str(excinfo.value) == "SNAPSHOT_MANIFEST_DIGEST_MISMATCH"


@pytest.mark.parametrize(
    ("field", "forged_value"),
    [
        ("source_revision_id", "revision:forged-after-capture"),
        ("source_sha256", "0" * 64),
        ("snapshot_manifest_sha256", "0" * 64),
        ("snapshot_id", "snapshot-forged"),
    ],
    ids=["revision", "source-digest", "manifest-digest", "snapshot-id"],
)
def test_tampered_evidence_provenance_fact_refuses_verification(
    tmp_path: Path, field: str, forged_value: str,
) -> None:
    """Editing an identity field without recomputing the canonical digest is refused."""
    store, _source, snapshot = _capture(
        tmp_path, CFR_BYTES, name=f"tamper-evidence-{field}",
    )
    evidence = _bind(store, snapshot).as_evidence()
    assert evidence[field] != forged_value
    forged = dict(evidence)
    forged[field] = forged_value

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, forged)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"


# ---------------------------------------------------------------------------
# Case 4: incorrect selected stream.
# ---------------------------------------------------------------------------


def test_selected_stream_index_out_of_range_refuses_binding(tmp_path: Path) -> None:
    """One video trak exists; asking for ordinal 1 is a measurement refusal."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="stream-out-of-range")

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot, stream_index=1)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED"


@pytest.mark.parametrize(
    "blob",
    [
        build_multi_trak_mp4(
            media_timescale=MEDIA_TIMESCALE,
            traks=[{"media_timescale": MEDIA_TIMESCALE, "sample_deltas": (40, 40, 40),
                    "handler": b"soun"}],
        ),
        build_multi_trak_mp4(
            media_timescale=MEDIA_TIMESCALE,
            traks=[
                {"media_timescale": MEDIA_TIMESCALE, "sample_deltas": (40, 40, 40),
                 "handler": b"soun"},
                {"media_timescale": MEDIA_TIMESCALE, "sample_deltas": (40, 40, 40),
                 "handler": b"vide"},
            ],
        ),
    ],
    ids=["audio-only", "audio-then-video"],
)
def test_selected_stream_index_pointing_at_non_video_trak_refuses_binding(
    tmp_path: Path, blob: bytes,
) -> None:
    """A timing-bearing but non-video ``trak`` is never an admissible stream mapping."""
    store, _source, snapshot = _capture(tmp_path, blob, name="non-video-stream")

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot, stream_index=0)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED"


def test_measured_stream_index_disagreement_refuses_binding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The receipt's selected ordinal must equal the parser's measured ordinal."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="stream-disagreement")
    _patched_parse(
        monkeypatch, lambda measured: measured.__setitem__("stream_index", 1),
    )

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot, stream_index=0)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_STREAM_MISMATCH"


# ---------------------------------------------------------------------------
# Case 5: missing or conflicting timescale.
# ---------------------------------------------------------------------------


def test_missing_measured_media_timescale_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="missing-timescale")
    _patched_parse(monkeypatch, lambda measured: measured.pop("media_timescale"))

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_FACTS_INVALID"


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("string", "1000"),
        ("bool", True),
        ("zero", 0),
        ("negative", -1000),
    ],
)
def test_wrong_typed_measured_media_timescale_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, label: str, value: object,
) -> None:
    """Timescale identity is an exact positive integer, never a coercible value."""
    store, _source, snapshot = _capture(
        tmp_path, CFR_BYTES, name=f"timescale-{label}",
    )
    _patched_parse(
        monkeypatch, lambda measured: measured.__setitem__("media_timescale", value),
    )

    with pytest.raises(SourceSnapshotError) as excinfo:
        _bind(store, snapshot)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_FACTS_INVALID"


def test_r3_route_blocks_time_base_that_does_not_match_named_bytes(tmp_path: Path) -> None:
    """The R3 tail route is cheaply callable and independently refuses a bad timebase."""
    from gate3.pts import PtsTable
    from gate3.rational import TimeBase
    from gate3.refinement import recompute_tail

    blob = build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12))
    source = tmp_path / "r3-source.mp4"
    source.write_bytes(blob)
    facts = parse_iso_bmff_timing_bytes(blob)
    digest = hashlib.sha256(blob).hexdigest()

    # Control: the canonical (1, media_timescale) table binds against the named bytes.
    ok, detail = recompute_tail(
        PtsTable(TimeBase(1, 25), tuple(facts["pts_ticks"])),
        50,
        source_content_digest=digest,
        stream_index=0,
        container_path=str(source),
    )
    assert ok is True
    assert detail["tail_end_ticks"] == 50

    # A timescale that disagrees with the measured bytes is blocked by name.
    ok, detail = recompute_tail(
        PtsTable(TimeBase(2, 25), tuple(facts["pts_ticks"])),
        50,
        source_content_digest=digest,
        stream_index=0,
        container_path=str(source),
    )
    assert ok is False
    assert detail["blocked"] == "TIME_BASE_DOES_NOT_MATCH_NAMED_BYTES"


# ---------------------------------------------------------------------------
# Case 10: missing or inconsistent duration / tail (PENDING A-12/IT-6).
# ---------------------------------------------------------------------------


def test_duration_inconsistent_source_currently_binds_and_issues_v1_evidence(
    tmp_path: Path,
) -> None:
    """PINNED CURRENT BEHAVIOUR (defect): a MISMATCH duration still binds.

    The parser measures ``duration_consistency == "MISMATCH"`` on these synthetic
    bytes; ``bind_temporal_authority`` ignores that fact entirely, so the source
    binds and the receipt still claims ``schema_version: 1`` authority.  This is
    the measured v1 defect versus the undecided tail policy (A-12/IT-6).  This
    test is deliberately GREEN so the defect is pinned rather than blurred; the
    corrected expectation lives in the strict-xfail tripwire below.
    """
    facts = parse_iso_bmff_timing_bytes(DURATION_INCONSISTENT_BYTES)
    assert facts["duration_ts"] == 999
    assert facts["pts_ticks"][-1] + facts["tail_duration_ticks"] == 160
    assert facts["duration_consistency"] == "MISMATCH"

    store, _source, snapshot = _capture(
        tmp_path, DURATION_INCONSISTENT_BYTES, name="duration-mismatch",
    )
    binding = _bind(store, snapshot)
    evidence = binding.as_evidence()

    assert evidence["schema_version"] == 1
    assert set(evidence) == _V1_EVIDENCE_FIELDS
    # The measured MISMATCH never survives into the receipt.
    assert "duration_consistency" not in evidence
    assert "duration_ts" not in evidence
    # The receipt round-trips through its own verifier despite the MISMATCH.
    rebound = store.verify_temporal_authority(snapshot, evidence)
    assert rebound.as_evidence() == evidence


@pytest.mark.xfail(
    strict=True,
    reason=(
        "A-12/IT-6 PENDING: duration/tail policy undecided; v1 binding ignores "
        "duration_consistency"
    ),
)
def test_duration_inconsistent_source_must_not_bind(tmp_path: Path) -> None:
    """Corrected expectation: a MISMATCH duration is not binding authority.

    A source whose ``mdhd`` duration contradicts ``presentation[-1] + tail`` has
    an unresolved tail extent, so the v1 binding must refuse rather than issue
    authoritative evidence.  Today it binds, so this test fails and is consumed
    by ``xfail(strict=True)``; it becomes ``XPASS(strict)`` (a real failure) the
    moment the tail policy is implemented and the refusal appears -- the intended
    tripwire.
    """
    facts = parse_iso_bmff_timing_bytes(DURATION_INCONSISTENT_BYTES)
    assert facts["duration_consistency"] == "MISMATCH"

    store, _source, snapshot = _capture(
        tmp_path, DURATION_INCONSISTENT_BYTES, name="duration-must-refuse",
    )
    with pytest.raises(SourceSnapshotError):
        _bind(store, snapshot)


# ---------------------------------------------------------------------------
# Case 11: missing or contradictory provenance facts.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "removed",
    ["schema_version", "source_revision_id", "timebase", "evidence_sha256"],
)
def test_removed_required_evidence_field_is_refused(
    tmp_path: Path, removed: str,
) -> None:
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name=f"remove-{removed}")
    evidence = _bind(store, snapshot).as_evidence()
    forged = dict(evidence)
    forged.pop(removed)

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, forged)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID"


@pytest.mark.parametrize(
    "v2_field",
    [
        ("composition_offsets", [0, 0, 0, 0]),
        ("presentation_origin_ticks", 0),
        ("duration_consistency", "MATCH"),
    ],
    ids=["composition-offsets", "presentation-origin", "duration-consistency"],
)
def test_added_v2_style_evidence_field_is_refused(
    tmp_path: Path, v2_field: tuple[str, object],
) -> None:
    """The frozen v1 field set refuses any v2 fact; extending it in place is forbidden."""
    field, value = v2_field
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name=f"add-{field}")
    evidence = _bind(store, snapshot).as_evidence()
    forged = dict(evidence)
    forged[field] = value

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, forged)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID"


def test_contradictory_snapshot_manifest_sha256_refuses_verification(
    tmp_path: Path,
) -> None:
    """A well-formed but wrong manifest digest is caught by canonical rebinding."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="contra-manifest")
    evidence = _bind(store, snapshot).as_evidence()
    forged = dict(evidence)
    forged["snapshot_manifest_sha256"] = "0" * 64

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, forged)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"


# ---------------------------------------------------------------------------
# Case 12: independent verification after serialization.
# ---------------------------------------------------------------------------


def test_json_round_trip_preserves_canonical_form_and_still_verifies(
    tmp_path: Path,
) -> None:
    """JSON serialize -> deserialize keeps lists; the receipt still verifies."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="round-trip")
    evidence = _bind(store, snapshot).as_evidence()

    reloaded = json.loads(json.dumps(evidence))
    # The canonical body is already JSON-native (lists, not tuples).
    assert isinstance(reloaded["pts_ticks"], list)
    assert isinstance(reloaded["dts_ticks"], list)
    assert reloaded == evidence

    binding = store.verify_temporal_authority(snapshot, reloaded)
    assert binding.as_evidence() == evidence
    assert binding.pts_ticks == (0, 40, 80, 120)


def test_byte_flipped_evidence_digest_refuses_verification(tmp_path: Path) -> None:
    """A digest-shaped but wrong ``evidence_sha256`` is detected by canonical rebinding."""
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="flipped-digest")
    evidence = _bind(store, snapshot).as_evidence()
    original = evidence["evidence_sha256"]
    flipped_first = "e" if original[0] != "e" else "f"
    forged = dict(evidence)
    forged["evidence_sha256"] = flipped_first + original[1:]
    assert len(forged["evidence_sha256"]) == 64

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, forged)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH"


def test_tuple_encoded_ticks_are_not_the_canonical_serialized_form(
    tmp_path: Path,
) -> None:
    """Measured finding: only JSON-native lists are accepted after deserialization.

    A Python-side "round trip" that restores tuples instead of JSON lists is
    refused at the type layer, so the normalizing/round-trip helper must be the
    canonical JSON encoding, not a generic object copy.
    """
    store, _source, snapshot = _capture(tmp_path, CFR_BYTES, name="tuple-encoded")
    evidence = _bind(store, snapshot).as_evidence()
    forged = dict(evidence)
    forged["pts_ticks"] = tuple(evidence["pts_ticks"])
    forged["dts_ticks"] = tuple(evidence["dts_ticks"])

    with pytest.raises(SourceSnapshotError) as excinfo:
        store.verify_temporal_authority(snapshot, forged)
    assert str(excinfo.value) == "SNAPSHOT_TEMPORAL_EVIDENCE_TYPES_INVALID"
