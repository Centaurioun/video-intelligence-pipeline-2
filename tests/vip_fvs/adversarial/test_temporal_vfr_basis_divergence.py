"""Adversarial evidence: snapshot VFR basis is decode order, authority is presentation order.

Governing authority
-------------------
Root G design (``docs/superpowers/specs/2026-09-25-root-g-real-source-temporal-revision-
closure-design.md``) section 3.5 "VFR rule":

    Variable-frame-rate sources are handled solely by their measured presentation
    ticks and validated timebase. ... Reordering (B-frames) is handled by
    presentation-order fields only; decode-order values are never endpoint authority.

``docs/architecture/CANONICAL_CONTRACTS.md`` section 4 "Typed interval envelope":
"VFR media may never derive source frames from ``seconds × FPS`` alone", and every
interval claim identifies its stream, timebase, and presentation origin.

Current snapshot behavior under test (``src/vip_fvs/source_snapshot.py``
``SourceSnapshotStore.bind_temporal_authority``) computes::

    durations = tuple(b - a for a, b in zip(dts, dts[1:])) + (tail,)
    observed_vfr = len(set(durations)) > 1

where ``dts`` is the decode-order enumeration and ``tail`` the last ``stts`` delta.
Because ``build_mp4``/``stts`` deltas are exactly the decode-order sample deltas,
that predicate reduces to ``len(set(sample_deltas)) > 1`` and is blind to any
``ctts`` composition offsets that change the *presentation* tick spacing.

The tests below are of three kinds:

1. **Measurement evidence (green).** Exact integer vectors measured from synthetic
   ISO-BMFF fixtures, both interval sets, and the two agreement controls.
2. **Corrected presentation-basis expectation (green, schema v2).** IT-2 is now
   implemented by the additive ``SourceSnapshotStore.bind_temporal_authority_v2``
   entry point (Owner-approved bounded A′-7 decision D-1..D-3), which classifies
   VFR from measured presentation PTS deltas only.  These assertions were captured
   as ``xfail(strict=True)`` while the correction was PENDING A-3/IT-2; they are now
   satisfied and must stay satisfied.
3. **Historical v1 refusal (green, preserved).** The schema-v1 entry point keeps its
   decode-order predicate byte-for-byte.  Under the same fixtures it still refuses
   the presentation-correct declaration and binds the decode-order one.  That
   historical behavior is preserved deliberately and must not be "fixed" for v1.

All input bytes are synthetic and deterministic (``gate3.fixturegen.build_mp4``);
no real media, network, model, or ffmpeg dependency is involved.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from gate3.container import parse_iso_bmff_timing_bytes
from gate3.fixturegen import build_mp4
from vip_fvs.source_snapshot import SourceSnapshotError, SourceSnapshotStore

MEDIA_TIMESCALE = 1000
TAIL_TICKS = 40
DURATION_TS = 160

# Case (i): uniform decode deltas (decode basis says CFR) with composition offsets
# that make the measured presentation interval set non-uniform (presentation says VFR).
CASE_I_DELTAS = (40, 40, 40, 40)
CASE_I_OFFSETS = (0, 80, 20, -60)

# Case (ii): non-uniform decode deltas (decode basis says VFR) with composition
# offsets that make the measured presentation interval set uniform (presentation says CFR).
CASE_II_DELTAS = (30, 50, 40, 40)
CASE_II_OFFSETS = (0, 50, -40, 0)

# Agreement controls: no composition offsets, so both bases must agree.
CFR_DELTAS = (40, 40, 40, 40)
VFR_DELTAS = (30, 50, 40, 40)

def _fixture_bytes(*, sample_deltas, ctts_offsets=None) -> bytes:
    return build_mp4(
        media_timescale=MEDIA_TIMESCALE,
        sample_deltas=sample_deltas,
        ctts_offsets=ctts_offsets,
    )


def _measure(blob: bytes) -> dict:
    """Measure the deterministic synthetic fixture with the production parser."""
    return parse_iso_bmff_timing_bytes(blob)


def _decode_basis_intervals(facts: dict) -> tuple[int, ...]:
    """The interval set the current snapshot predicate uses: dts diffs + last stts delta."""
    dts = facts["dts_ticks"]
    return tuple(b - a for a, b in zip(dts, dts[1:])) + (facts["tail_duration_ticks"],)


def _presentation_basis_intervals(facts: dict) -> tuple[int, ...]:
    """Presentation-basis intervals from measured facts only.

    ``pts_ticks`` is the parser's retained, sorted presentation enumeration.  The
    presentation tail is derived from the measured last ``stts`` delta
    (``tail_duration_ticks``, the duration of the sample that ends the stream) and
    is admissible only because the parser independently corroborates the mapping
    span: ``pts_ticks[-1] + tail_duration_ticks == duration_ts`` (asserted by the
    measurement tests below).  If ``duration_ts`` were absent the presentation
    tail would be ``NOT_OBSERVED`` and this interval set could not be formed; the
    parser always emits an integer ``duration_ts`` for these fixtures.
    """
    pts = facts["pts_ticks"]
    return tuple(b - a for a, b in zip(pts, pts[1:])) + (facts["tail_duration_ticks"],)


def _is_vfr(intervals: tuple[int, ...]) -> bool:
    return len(set(intervals)) > 1


def _capture(tmp_path: Path, blob: bytes, *, name: str):
    source = tmp_path / f"{name}.mp4"
    source.write_bytes(blob)
    store = SourceSnapshotStore(
        tmp_path / f"store-{name}",
        max_source_bytes=max(64_000, len(blob) * 2),
        max_store_bytes=max(256_000, len(blob) * 8),
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(blob).hexdigest(),
        authorization_id="authorization:synthetic-vfr-basis",
        source_revision_id="revision:synthetic-vfr-basis",
    )
    return store, snapshot


# ---------------------------------------------------------------------------
# Measurement evidence: exact integer divergence, both directions.
# ---------------------------------------------------------------------------


def test_case_i_decode_basis_cfr_presentation_basis_vfr_exact_integers() -> None:
    """Uniform stts + varying ctts: decode says CFR, presentation says VFR."""
    facts = _measure(_fixture_bytes(sample_deltas=CASE_I_DELTAS, ctts_offsets=CASE_I_OFFSETS))

    assert facts["media_timescale"] == MEDIA_TIMESCALE
    assert facts["dts_ticks"] == (0, 40, 80, 120)
    assert facts["pts_ticks"] == (0, 60, 100, 120)
    assert facts["composition_offsets"] == (0, 80, 20, -60)
    assert facts["tail_duration_ticks"] == TAIL_TICKS
    assert facts["duration_ts"] == DURATION_TS
    assert facts["duration_consistency"] == "MATCH"
    assert facts["has_b_frames"] == 1
    assert facts["nb_frames"] == 4

    decode_intervals = _decode_basis_intervals(facts)
    presentation_intervals = _presentation_basis_intervals(facts)
    assert decode_intervals == (40, 40, 40, 40)
    assert presentation_intervals == (60, 40, 20, 40)
    assert _is_vfr(decode_intervals) is False
    assert _is_vfr(presentation_intervals) is True
    assert decode_intervals != presentation_intervals
    # Presentation mapping span is corroborated by the measured media duration.
    assert facts["pts_ticks"][-1] + facts["tail_duration_ticks"] == facts["duration_ts"]


def test_case_ii_decode_basis_vfr_presentation_basis_cfr_exact_integers() -> None:
    """Varying stts + compensating ctts: decode says VFR, presentation says CFR."""
    facts = _measure(_fixture_bytes(sample_deltas=CASE_II_DELTAS, ctts_offsets=CASE_II_OFFSETS))

    assert facts["media_timescale"] == MEDIA_TIMESCALE
    assert facts["dts_ticks"] == (0, 30, 80, 120)
    assert facts["pts_ticks"] == (0, 40, 80, 120)
    assert facts["composition_offsets"] == (0, 50, -40, 0)
    assert facts["tail_duration_ticks"] == TAIL_TICKS
    assert facts["duration_ts"] == DURATION_TS
    assert facts["duration_consistency"] == "MATCH"
    assert facts["has_b_frames"] == 1
    assert facts["nb_frames"] == 4

    decode_intervals = _decode_basis_intervals(facts)
    presentation_intervals = _presentation_basis_intervals(facts)
    assert decode_intervals == (30, 50, 40, 40)
    assert presentation_intervals == (40, 40, 40, 40)
    assert _is_vfr(decode_intervals) is True
    assert _is_vfr(presentation_intervals) is False
    assert decode_intervals != presentation_intervals
    assert facts["pts_ticks"][-1] + facts["tail_duration_ticks"] == facts["duration_ts"]


def test_control_plain_cfr_bases_agree_and_binding_accepts_cfr() -> None:
    """No ctts: decode and presentation interval sets are identical; binding accepts CFR."""
    blob = _fixture_bytes(sample_deltas=CFR_DELTAS)
    facts = _measure(blob)
    assert facts["dts_ticks"] == (0, 40, 80, 120)
    assert facts["pts_ticks"] == facts["dts_ticks"]
    assert facts["has_b_frames"] == 0
    decode_intervals = _decode_basis_intervals(facts)
    presentation_intervals = _presentation_basis_intervals(facts)
    assert decode_intervals == presentation_intervals == (40, 40, 40, 40)
    assert _is_vfr(decode_intervals) is _is_vfr(presentation_intervals) is False
    assert facts["pts_ticks"][-1] + facts["tail_duration_ticks"] == facts["duration_ts"]


def test_control_plain_vfr_bases_agree() -> None:
    """No ctts, varying stts: both bases classify VFR identically (no divergence to capture)."""
    facts = _measure(_fixture_bytes(sample_deltas=VFR_DELTAS))
    assert facts["dts_ticks"] == (0, 30, 80, 120)
    assert facts["pts_ticks"] == facts["dts_ticks"]
    assert facts["has_b_frames"] == 0
    decode_intervals = _decode_basis_intervals(facts)
    presentation_intervals = _presentation_basis_intervals(facts)
    assert decode_intervals == presentation_intervals == (30, 50, 40, 40)
    assert _is_vfr(decode_intervals) is _is_vfr(presentation_intervals) is True


# ---------------------------------------------------------------------------
# Binding controls (stable both before and after the predicate fix).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sample_deltas,declared_vfr",
    [(CFR_DELTAS, False), (VFR_DELTAS, True)],
    ids=["cfr", "vfr"],
)
def test_control_agreeing_declarations_bind_and_persist_declaration(
    tmp_path: Path, sample_deltas: tuple[int, ...], declared_vfr: bool,
) -> None:
    """Where both bases agree, the binding accepts and persists the declaration."""
    blob = _fixture_bytes(sample_deltas=sample_deltas)
    facts = _measure(blob)
    assert _is_vfr(_decode_basis_intervals(facts)) is declared_vfr
    assert _is_vfr(_presentation_basis_intervals(facts)) is declared_vfr

    store, snapshot = _capture(tmp_path, blob, name=f"control-{'vfr' if declared_vfr else 'cfr'}")
    binding = store.bind_temporal_authority(
        snapshot,
        selected_stream_index=0,
        declared_vfr=declared_vfr,
        declared_reordering=False,
    )
    assert binding.declared_vfr is declared_vfr
    assert binding.declared_reordering is False
    assert binding.pts_ticks == facts["pts_ticks"]
    assert binding.dts_ticks == facts["dts_ticks"]
    assert binding.timebase_den == MEDIA_TIMESCALE


# ---------------------------------------------------------------------------
# IT-2 correction: presentation PTS deltas govern schema-v2 VFR classification.
# ---------------------------------------------------------------------------


def test_presentation_basis_vfr_governs_when_decode_basis_is_cfr(tmp_path: Path) -> None:
    """A declaration that only agrees with decode order must not bind in v2.

    Measured facts: decode intervals ``(40,40,40,40)`` (CFR) but presentation
    intervals ``(60,40,20,40)`` (VFR).  Root G section 3.5 requires the binding to
    classify VFR from presentation ticks, so ``declared_vfr=False`` is refused and
    ``declared_vfr=True`` binds -- in the additive schema-v2 entry point.
    """
    blob = _fixture_bytes(sample_deltas=CASE_I_DELTAS, ctts_offsets=CASE_I_OFFSETS)
    facts = _measure(blob)
    # Preconditions: the divergence itself is measured, not assumed.
    assert _is_vfr(_decode_basis_intervals(facts)) is False
    assert _is_vfr(_presentation_basis_intervals(facts)) is True

    store, snapshot = _capture(tmp_path, blob, name="presentation-vfr")
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_VFR_DECLARATION_MISMATCH"):
        store.bind_temporal_authority_v2(
            snapshot,
            selected_stream_index=0,
            declared_vfr=False,
            declared_reordering=True,
        )
    binding = store.bind_temporal_authority_v2(
        snapshot,
        selected_stream_index=0,
        declared_vfr=True,
        declared_reordering=True,
    )
    assert binding.declared_vfr is True
    assert binding.as_evidence()["schema_version"] == 2
    assert binding.pts_ticks == facts["pts_ticks"] == (0, 60, 100, 120)
    assert binding.dts_ticks == facts["dts_ticks"] == (0, 40, 80, 120)
    assert binding.composition_offsets == CASE_I_OFFSETS


def test_presentation_basis_cfr_governs_when_decode_basis_is_vfr(tmp_path: Path) -> None:
    """The symmetric direction: presentation CFR must not inherit decode-order VFR.

    Measured facts: decode intervals ``(30,50,40,40)`` (VFR) but presentation
    intervals ``(40,40,40,40)`` (CFR).  ``declared_vfr=True`` is refused and
    ``declared_vfr=False`` binds in schema v2.
    """
    blob = _fixture_bytes(sample_deltas=CASE_II_DELTAS, ctts_offsets=CASE_II_OFFSETS)
    facts = _measure(blob)
    assert _is_vfr(_decode_basis_intervals(facts)) is True
    assert _is_vfr(_presentation_basis_intervals(facts)) is False

    store, snapshot = _capture(tmp_path, blob, name="presentation-cfr")
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_VFR_DECLARATION_MISMATCH"):
        store.bind_temporal_authority_v2(
            snapshot,
            selected_stream_index=0,
            declared_vfr=True,
            declared_reordering=True,
        )
    binding = store.bind_temporal_authority_v2(
        snapshot,
        selected_stream_index=0,
        declared_vfr=False,
        declared_reordering=True,
    )
    assert binding.declared_vfr is False
    assert binding.as_evidence()["schema_version"] == 2
    assert binding.pts_ticks == facts["pts_ticks"] == (0, 40, 80, 120)
    assert binding.dts_ticks == facts["dts_ticks"] == (0, 30, 80, 120)
    assert binding.composition_offsets == CASE_II_OFFSETS


# ---------------------------------------------------------------------------
# Historical v1 refusal behavior is preserved, not "fixed".
# ---------------------------------------------------------------------------


def test_legacy_v1_predicate_still_uses_decode_order_and_tail(tmp_path: Path) -> None:
    """Schema v1 keeps its historical decode-order VFR predicate byte-for-byte.

    ``bind_temporal_authority`` must remain usable by existing v1 consumers, so it
    still classifies from ``dts`` deltas plus the last ``stts`` delta.  Under case
    (i) that means the decode-only declaration binds and the presentation-correct
    declaration is refused; a future v2-only consumer refuses v1 explicitly under
    its own PENDING A-5 refusal-code decision.
    """
    blob = _fixture_bytes(sample_deltas=CASE_I_DELTAS, ctts_offsets=CASE_I_OFFSETS)
    facts = _measure(blob)
    assert _is_vfr(_decode_basis_intervals(facts)) is False
    assert _is_vfr(_presentation_basis_intervals(facts)) is True

    store, snapshot = _capture(tmp_path, blob, name="legacy-v1-decode-basis")
    legacy = store.bind_temporal_authority(
        snapshot,
        selected_stream_index=0,
        declared_vfr=False,
        declared_reordering=True,
    )
    assert legacy.declared_vfr is False
    assert legacy.as_evidence()["schema_version"] == 1
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_VFR_DECLARATION_MISMATCH"):
        store.bind_temporal_authority(
            snapshot,
            selected_stream_index=0,
            declared_vfr=True,
            declared_reordering=True,
        )
    # The v1 receipt still verifies: the historical behavior is internally consistent.
    assert store.verify_temporal_authority(
        snapshot, legacy.as_evidence()
    ).as_evidence() == legacy.as_evidence()
