"""Gate-3 / source-snapshot temporal-safety adversarial coverage.

These tests pin one load-bearing invariant from several sides: **source-native
PTS/timebase is the only temporal binding authority**.  A snapshot may only bind
the temporal identity it re-measured from its own retained bytes, a nominal frame
rate (25 fps style arithmetic) can never produce an admitted source position, a
``semantic_seconds`` candidate can never be promoted to a source-exact class, and
a measured record can never be relabelled into a weaker evidence class.

Fixtures are synthetic ISO-BMFF containers built by ``gate3.fixturegen`` only;
no real media, network, provider or model call is involved.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import stat
import struct

import pytest

import gate3.authority as gate3_authority
import vip_fvs.real_source_service as real_source_service
import vip_fvs.refinement_adapter as refinement_adapter
from gate3.container import parse_iso_bmff_timing
from gate3.fixturegen import build_mp4
from gate3.pts import PtsTable
from gate3.rational import TimeBase
from gate3.refinement import (
    BINDING_CHECK,
    is_binding_eligible,
    is_structurally_eligible,
    refine,
)
from gate3.refinement_request import RefinementRequest
from vip_fvs.refinement_adapter import RefinementRefusal, refine_retrieval_candidate
from vip_fvs.source_snapshot import SourceSnapshotError, SourceSnapshotStore

VFR_DELTAS = (400, 200, 600, 200)
VFR_TIMESCALE = 1000
# 25 fps expressed in the fixture's 1/1000 media timebase: frame ``i`` would land on 40*i.
NOMINAL_25FPS_FRAME_TICKS = 40

# Measured container facts sealed by schema v2 (A'-7 D-2) plus the deliberately
# excluded ``nb_frames``.  These may be read from the authenticated parser result
# and serialized into the closed evidence dict; they may never be *derived* from a
# nominal frame rate nor arithmetically positioned.
_MEASURED_CONTAINER_FACT_KEYS = (
    "duration_ts",
    "duration_consistency",
    "tail_duration_ticks",
    "presentation_origin_ticks",
    "stream_handler",
    "stream_identity_derivation",
    "composition_offsets",
    "nb_frames",
)
_NOMINAL_RATE_TOKENS = ("fps", "frame_rate", "nominal", "declared_rate")
_STRING_LITERAL = re.compile(r'"[^"]*"|\'[^\']*\'')
_FACT_KEYS = frozenset(_MEASURED_CONTAINER_FACT_KEYS)
_SERIES_READ_ATTRS = ("get", "setdefault")
_EXPRESSION_NODES = (
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.Call,
    ast.Subscript,
    ast.Attribute,
    ast.JoinedStr,
    ast.AugAssign,
    ast.Tuple,
    ast.List,
    ast.Set,
    ast.Dict,
)


def _measured_fact_reads(node: ast.AST) -> bool:
    """True if ``node`` reads a sealed measured fact as a value."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) and sub.attr in _FACT_KEYS:
            return True
        if (isinstance(sub, ast.Subscript)
                and isinstance(sub.slice, ast.Constant)
                and isinstance(sub.slice.value, str)
                and sub.slice.value in _FACT_KEYS):
            return True
        if (isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Attribute)
                and sub.func.attr in _SERIES_READ_ATTRS
                and sub.args
                and isinstance(sub.args[0], ast.Constant)
                and isinstance(sub.args[0].value, str)
                and sub.args[0].value in _FACT_KEYS):
            return True
    return False


def _contains_name(node: ast.AST, names: set[str]) -> bool:
    return any(isinstance(sub, ast.Name) and sub.id in names for sub in ast.walk(node))


def _expr_derives_from_fact(node: ast.AST, tainted: set[str]) -> bool:
    return _measured_fact_reads(node) or _contains_name(node, tainted)


def _reads_parser_series(node: ast.AST) -> bool:
    """True if ``node`` copies authenticated parser output (series/collection read)."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Subscript):
            return True
        if (isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Attribute)
                and sub.func.attr in _SERIES_READ_ATTRS):
            return True
    return False


def _contains_parser_series(node: ast.AST, parser_names: set[str]) -> bool:
    return _reads_parser_series(node) or _contains_name(node, parser_names)


def _dataflow_sets(tree: ast.AST) -> tuple[set[str], set[str], set[str]]:
    """Return ``(tainted, parser_names, field_set_names)`` by a fail-closed fixpoint.

    ``tainted`` names hold a value derived from a sealed measured fact (directly
    or through another alias); ``parser_names`` hold authenticated parser output
    (necessarily broader, and used only to allow measured↔parser validation
    arithmetic); ``field_set_names`` hold closed field-set declarations whose
    members are fact keys, so iterating one yields fact-key names (a loop/comp
    target over such a set is itself tainted).  A comprehension/loop target over
    tainted input is itself tainted.
    """
    tainted: set[str] = set()
    parser_names: set[str] = set()
    field_set_names: set[str] = set()

    def add(name: str, into: set[str]) -> bool:
        if name in into:
            return False
        into.add(name)
        return True

    def is_field_set_declaration(node: ast.Assign) -> bool:
        targets = [t for t in node.targets if isinstance(t, ast.Name) and t.id.isupper()]
        if not targets:
            return False
        if _is_closed_field_set(node.value):
            return any(
                isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                and sub.value in _FACT_KEYS
                for sub in ast.walk(node.value)
            )
        if isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.BitOr):
            return _contains_name(node.value, field_set_names)
        return False

    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            targets: list[ast.AST] = []
            value: ast.AST | None = None
            iter_all_caps = False
            if isinstance(node, ast.Assign):
                targets, value = list(node.targets), node.value
                if is_field_set_declaration(node):
                    for target in targets:
                        changed = add(target.id, field_set_names) or changed
            elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)):
                if node.value is not None:
                    targets, value = [node.target], node.value
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                targets, value = [node.target], node.iter
                # A loop over a module-level constant may be yielding fact keys
                # (e.g. iterating a field-set declaration); fail closed and treat
                # the loop target as fact-derived.
                iter_all_caps = isinstance(node.iter, ast.Name) and node.iter.id.isupper()
            elif isinstance(node, ast.withitem):
                if node.optional_vars is not None:
                    targets, value = [node.optional_vars], node.context_expr
            if value is None:
                continue
            fact_value = (
                _expr_derives_from_fact(value, tainted)
                or _contains_name(value, field_set_names)
                or iter_all_caps
            )
            parser_value = _reads_parser_series(value) or _contains_name(value, parser_names)
            for target in targets:
                for sub in ast.walk(target):
                    if not isinstance(sub, ast.Name):
                        continue
                    if fact_value:
                        changed = add(sub.id, tainted) or changed
                    if parser_value:
                        changed = add(sub.id, parser_names) or changed
    return tainted, parser_names, field_set_names


_COLLECTION_CTORS = frozenset({"frozenset", "set", "tuple", "list", "dict"})


def _is_closed_field_set(node: ast.AST) -> bool:
    """True for a collection literal/constructor that may name fact keys."""

    if isinstance(node, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
        return True
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _COLLECTION_CTORS
    )


def _assert_measured_facts_never_nominal_rate_derived(module_name: str, source: str) -> None:
    """Bounded AST/dataflow gate for read/serialize-only use of measured facts.

    This is a *static syntactic* control, deliberately not a provenance proof: it
    parses the module, computes a def-use taint set for values derived from the
    sealed v2 measured facts, and fails closed on the mechanically detectable
    shapes a nominal-rate derivation takes -- unit-scaling arithmetic on a tainted
    value, subtraction of a tainted value, addition of a tainted value to anything
    that is not authenticated parser output, a nominal-rate token in the same
    expression as a tainted value, dynamic construction of a fact key, iteration
    over a module-level constant that may hold fact keys, or a fact key literal
    used outside a recognised read/serialization role.  Aliases, annotations,
    renames, and comments are all handled, so the two-step bypass the previous
    line scanner accepted cannot survive a rename.

    It does not and cannot prove where a value came from.  Provenance rests on the
    sealed re-measurement in ``vip_fvs.source_snapshot`` and on the behavioral
    tamper controls in this module and
    ``tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py``.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:  # fail closed: unparseable source is never "safe"
        raise AssertionError(
            f"{module_name}: source is not parseable as Python, refusing to certify it: {exc}"
        ) from exc

    tainted, parser_names, field_set_names = _dataflow_sets(tree)

    # A fact key is only a fact key literal in a recognised role.  Anything else
    # (a variable assignment, getattr dispatch, ...) is refused rather than guessed.
    allowed_literal_ids: set[int] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
                and node.slice.value in _FACT_KEYS):
            allowed_literal_ids.add(id(node.slice))
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _SERIES_READ_ATTRS
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value in _FACT_KEYS):
            allowed_literal_ids.add(id(node.args[0]))
        if isinstance(node, ast.Dict):
            for key in node.keys:
                if (isinstance(key, ast.Constant) and isinstance(key.value, str)
                        and key.value in _FACT_KEYS):
                    allowed_literal_ids.add(id(key))
        if isinstance(node, ast.Assign):
            # A module-level closed field-set declaration is the one place a bare
            # fact-key string literal legitimately stands alone.  It must be a
            # collection literal/constructor, not a scalar alias of the key.
            if (any(isinstance(t, ast.Name) and t.id.isupper() for t in node.targets)
                    and _is_closed_field_set(node.value)):
                for sub in ast.walk(node.value):
                    if (isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                            and sub.value in _FACT_KEYS):
                        allowed_literal_ids.add(id(sub))

    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            slice_ = node.slice
            if isinstance(slice_, ast.JoinedStr) or (
                isinstance(slice_, ast.BinOp)
                and any(isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                        for sub in ast.walk(slice_))
            ):
                assert False, (
                    f"{module_name}: dynamically constructs a container key; measured "
                    f"fact reads must use a literal key (fail closed)"
                )
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and node.value in _FACT_KEYS and id(node) not in allowed_literal_ids):
            assert False, (
                f"{module_name}: measured fact key {node.value!r} is used outside a "
                f"recognised read/serialization role (fail closed)"
            )

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            left = _expr_derives_from_fact(node.left, tainted)
            right = _expr_derives_from_fact(node.right, tainted)
            if not (left or right):
                continue
            assert not isinstance(node.op, (ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)), (
                f"{module_name}:{node.lineno} scales a measured container fact "
                f"({type(node.op).__name__}); measured facts are never unit-scaled"
            )
            assert not isinstance(node.op, ast.Sub), (
                f"{module_name}:{node.lineno} arithmetically repositions a measured "
                f"container fact by subtraction"
            )
            if isinstance(node.op, ast.Add):
                if left and right:
                    continue
                other = node.right if left else node.left
                # Text concatenation of a serialized evidence string is not a
                # numeric position derivation (the nominal-token check still runs).
                if isinstance(other, ast.Constant) and isinstance(other.value, str):
                    continue
                assert _contains_parser_series(other, parser_names), (
                    f"{module_name}:{node.lineno} adds a measured container fact to a "
                    f"value that is not authenticated parser output"
                )
        elif isinstance(node, ast.AugAssign):
            target_tainted = _expr_derives_from_fact(node.target, tainted)
            value_tainted = _expr_derives_from_fact(node.value, tainted)
            if not (target_tainted or value_tainted):
                continue
            assert isinstance(node.op, ast.Add), (
                f"{module_name}:{node.lineno} applies {type(node.op).__name__} to a "
                f"measured container fact"
            )
            other = node.value if target_tainted else node.target
            assert (target_tainted and value_tainted) or _contains_parser_series(
                other, parser_names
            ), (
                f"{module_name}:{node.lineno} adds a measured container fact to a value "
                f"that is not authenticated parser output"
            )
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            assert not _expr_derives_from_fact(node.operand, tainted), (
                f"{module_name}:{node.lineno} applies unary {type(node.op).__name__} to "
                f"a measured container fact"
            )

    # A nominal-rate token may not share an expression with a tainted value, even
    # when the arithmetic shape alone is one the gate tolerates.
    for node in ast.walk(tree):
        if not isinstance(node, _EXPRESSION_NODES):
            continue
        if not _expr_derives_from_fact(node, tainted):
            continue
        segment = ast.get_source_segment(source, node) or ""
        code_only = _STRING_LITERAL.sub("", segment).lower()
        for token in _NOMINAL_RATE_TOKENS:
            assert token not in code_only, (
                f"{module_name}:{node.lineno} couples a measured container fact to "
                f"nominal rate token {token!r}"
            )


def _vfr_bytes(*, deltas=VFR_DELTAS, **kwargs) -> bytes:
    return build_mp4(media_timescale=VFR_TIMESCALE, sample_deltas=deltas, **kwargs)


def _capture(tmp_path: Path, source_bytes: bytes, *, name: str = "generated-vfr.mp4"):
    """Write synthetic bytes, ingest them into a store, return (store, source, snapshot)."""
    source = tmp_path / name
    source.write_bytes(source_bytes)
    store = SourceSnapshotStore(
        tmp_path / "snapshot-store", max_source_bytes=64_000, max_store_bytes=128_000,
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(source_bytes).hexdigest(),
        authorization_id=f"authorization:{name}",
        source_revision_id=f"revision:{name}",
    )
    return store, source, snapshot


def _request_identity(source: Path, facts, start: int, end: int, *, attempt_id: str = "attempt-1"):
    """Build the canonical Gate-3 refinement request identity for measured endpoints."""
    request = {
        "request_id": "request-1",
        "candidate_assertion_ref": "assertion-1",
        "source_revision_id": "revision:generated-vfr.mp4",
        "source_locator": str(source),
        "expected_source_sha256": facts["source_bytes_sha256"],
        "selected_stream_index": facts["stream_index"],
        "requested_start_pts": start,
        "requested_end_pts": end,
        "producer_attempt_id": attempt_id,
        "idempotency_key": "idempotency-1",
        "expected_timebase": None,
    }
    return {
        "request_id": request["request_id"],
        "candidate_assertion_ref": request["candidate_assertion_ref"],
        "producer_attempt_id": request["producer_attempt_id"],
        "idempotency_key": request["idempotency_key"],
        "request_digest": hashlib.sha256(
            gate3_authority.canonical_json(request).encode("utf-8")
        ).hexdigest(),
        "request": request,
    }


def _refine_measured(source: Path, facts, start: int, end: int, *, declared_rate=None):
    """Run Gate-3 refinement against named synthetic bytes and measured endpoints."""
    return refine(
        PtsTable(TimeBase(1, facts["media_timescale"]), tuple(facts["pts_ticks"])),
        (start, end),
        attempt_id="attempt-1",
        tool_identity={"tool": "synthetic-temporal-safety"},
        time_domain="source_pts",
        precision="source-pts",
        source_revision_id="revision:generated-vfr.mp4",
        source_content_digest=facts["source_bytes_sha256"],
        stream_index=facts["stream_index"],
        declared_rate=declared_rate,
        container_path=str(source),
        request_identity=_request_identity(source, facts, start, end),
    )


def _refinement_hit(source: Path, facts) -> dict:
    return {
        "source_path": str(source),
        "source_sha256": facts["source_bytes_sha256"],
        "source_revision_id": "revision:generated-vfr.mp4",
        "rank": 1,
        "score": 0.9,
    }


def _truncate_leaf(container: bytes, kind: bytes, *, remove: int) -> bytes:
    """Remove bytes from one leaf box and keep every enclosing ISO-BMFF size consistent."""
    start = container.index(kind) - 4
    size = struct.unpack_from(">I", container, start)[0]
    assert size > 8 + remove
    result = bytearray(container[:start + size - remove] + container[start + size:])
    struct.pack_into(">I", result, start, size - remove)
    parents = {
        b"mdhd": (b"moov", b"trak", b"mdia"),
        b"stts": (b"moov", b"trak", b"mdia", b"minf", b"stbl"),
        b"ctts": (b"moov", b"trak", b"mdia", b"minf", b"stbl"),
        b"elst": (b"moov", b"trak", b"edts"),
    }[kind]
    for parent in parents:
        parent_start = container.index(parent) - 4
        parent_size = struct.unpack_from(">I", container, parent_start)[0]
        struct.pack_into(">I", result, parent_start, parent_size - remove)
    return bytes(result)


def _inflate_stts_entry_count(container: bytes) -> bytes:
    """Declare one more timing entry than the stts box actually contains."""
    result = bytearray(container)
    stts_start = result.index(b"stts") - 4
    count_offset = stts_start + 8 + 4
    count = struct.unpack_from(">I", result, count_offset)[0]
    struct.pack_into(">I", result, count_offset, count + 1)
    return bytes(result)


# ---------------------------------------------------------------------------
# 1. Source-native PTS/timebase is the only binding authority.
# ---------------------------------------------------------------------------


def test_snapshot_binds_only_measured_pts_and_media_timebase(tmp_path: Path) -> None:
    store, source, snapshot = _capture(tmp_path, _vfr_bytes())
    measured = parse_iso_bmff_timing(source)

    binding = store.bind_temporal_authority(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
    )

    assert measured["pts_ticks"] == (0, 400, 600, 1200)
    assert binding.pts_ticks == measured["pts_ticks"]
    assert binding.dts_ticks == measured["dts_ticks"] == (0, 400, 600, 1200)
    assert (binding.timebase_num, binding.timebase_den) == (1, measured["media_timescale"])
    assert (binding.timebase_num, binding.timebase_den) == (1, 1000)
    assert binding.source_sha256 == measured["source_bytes_sha256"] == snapshot.sha256
    # Variable inter-frame spacing is measured, not assumed.
    durations = tuple(b - a for a, b in zip(binding.dts_ticks, binding.dts_ticks[1:])) + (
        measured["tail_duration_ticks"],
    )
    assert durations == (400, 200, 600, 200)
    assert len(set(durations)) > 1
    # The evidence round-trips only against the same retained bytes.
    assert store.verify_temporal_authority(snapshot, binding.as_evidence()) == binding
    # No caller-supplied position is even accepted as an input to the binding call.
    parameters = inspect.signature(store.bind_temporal_authority).parameters
    assert set(parameters) == {
        "snapshot", "selected_stream_index", "declared_vfr", "declared_reordering",
    }


def test_snapshot_binds_measured_decode_order_separately_from_presentation(tmp_path: Path) -> None:
    store, source, snapshot = _capture(
        tmp_path, _vfr_bytes(ctts_offsets=(0, 400, -200, 0)),
    )
    measured = parse_iso_bmff_timing(source)

    binding = store.bind_temporal_authority(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=True,
    )

    assert measured["composition_offsets"] == (0, 400, -200, 0)
    assert binding.pts_ticks == (0, 400, 800, 1200)
    assert binding.dts_ticks == (0, 400, 600, 1200)
    assert binding.pts_ticks != binding.dts_ticks
    assert binding.declared_reordering is True
    assert store.verify_temporal_authority(snapshot, binding.as_evidence()) == binding


# ---------------------------------------------------------------------------
# 2. Nominal-FPS arithmetic is never an accepted temporal derivation.
# ---------------------------------------------------------------------------


def test_nominal_25fps_frame_times_disagree_with_measured_vfr_timing(tmp_path: Path) -> None:
    store, source, snapshot = _capture(tmp_path, _vfr_bytes())
    binding = store.bind_temporal_authority(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
    )

    nominal_frame_ticks = tuple(
        index * NOMINAL_25FPS_FRAME_TICKS for index in range(len(binding.pts_ticks))
    )

    assert nominal_frame_ticks == (0, 40, 80, 120)
    assert nominal_frame_ticks != binding.pts_ticks
    assert not set(nominal_frame_ticks).issubset(set(binding.pts_ticks))
    # The measured spacing is genuinely non-constant: no single nominal delta fits.
    measured_deltas = tuple(b - a for a, b in zip(binding.pts_ticks, binding.pts_ticks[1:]))
    assert measured_deltas == (400, 200, 600)
    assert len(set(measured_deltas)) == 3


def test_nominal_fps_position_is_refused_as_a_source_endpoint(tmp_path: Path) -> None:
    _, source, _ = _capture(tmp_path, _vfr_bytes())
    facts = parse_iso_bmff_timing(source)
    nominal_tick = NOMINAL_25FPS_FRAME_TICKS  # 25 fps frame 1 in 1/1000 ticks

    blocked = _refine_measured(source, facts, nominal_tick, 400)

    assert blocked == {"blocked": "ENDPOINT_NOT_A_PTS_MEMBER"}
    with pytest.raises(RefinementRefusal, match="requested start endpoint is not a measured source PTS"):
        refine_retrieval_candidate(
            _refinement_hit(source, facts),
            source_revision_id="revision:generated-vfr.mp4",
            requested_pts=(nominal_tick, 400),
            attempt_id="attempt-1",
        )

    # Control: the same request against a genuinely measured endpoint is admitted,
    # so the refusal above is positional rather than a digest or provenance refusal.
    admitted = refine_retrieval_candidate(
        _refinement_hit(source, facts),
        source_revision_id="revision:generated-vfr.mp4",
        requested_pts=(400, 600),
        attempt_id="attempt-1",
    )
    assert admitted.binding_eligible is True
    assert admitted.measured_refinement["start_ticks"] == 400
    assert admitted.measured_refinement["end_ticks"] == 600


# ---------------------------------------------------------------------------
# 3. No nominal-rate field is consulted to derive positions.
# ---------------------------------------------------------------------------


def test_temporal_authority_modules_never_consult_nominal_rate_fields() -> None:
    nominal_rate_fields = ("r_frame_rate", "avg_frame_rate")
    boundary_modules = (
        "vip_fvs.source_snapshot",
        "vip_fvs.real_source_probe",
        "vip_fvs.refinement_adapter",
        "gate3.refinement",
    )
    sources = {
        name: inspect.getsource(__import__(name, fromlist=["_"])) for name in boundary_modules
    }
    for name, source in sources.items():
        for token in nominal_rate_fields:
            assert token not in source, f"{name} consults nominal rate field {token!r}"

    # `duration_ts` and its six sibling facts are now SEALED v2 measured facts
    # (A'-7 D-2), so their presence is expected and legitimate at the binding
    # boundary -- but only as authenticated parser-result reads or closed
    # evidence-dict serialization.  The excluded `nb_frames` stays absent.
    for name in ("vip_fvs.source_snapshot", "vip_fvs.real_source_probe", "vip_fvs.refinement_adapter"):
        assert "nb_frames" not in sources[name], (
            f"{name} uses measured container fact 'nb_frames' (excluded from the "
            f"approved v2 payload; it is derivable as len(pts_ticks))"
        )
        _assert_measured_facts_never_nominal_rate_derived(name, sources[name])

    # In gate3.refinement those facts only ever flow from re-measured container
    # facts (never re-derived from a declared rate).
    provenance_markers = ("facts", "container", "enumerated", "derivation", "DERIVATION", "record")
    for line in sources["gate3.refinement"].splitlines():
        if "nb_frames" in line or "duration_ts" in line:
            assert any(marker in line for marker in provenance_markers), line


def test_measured_fact_structural_gate_rejects_nominal_rate_derivations() -> None:
    """The structural gate is not vacuous: read/serialize passes, derivation fails."""
    good = (
        'measured_duration = facts["duration_ts"]\n'
        'body = {"duration_ts": measured_duration}\n'
        'offsets = evidence["composition_offsets"]\n'
        'derivation = facts["stream_identity_derivation"]\n'
    )
    _assert_measured_facts_never_nominal_rate_derived("synthetic.good", good)
    for bad in (
        'frame_ticks = facts["duration_ts"] * nominal_rate\n',
        'start = facts["tail_duration_ticks"] // computed_fps\n',
        'positions = round(declared_rate * facts["duration_ts"])\n',
        'count = len(facts["composition_offsets"]) + 1 * fps\n',
    ):
        with pytest.raises(AssertionError):
            _assert_measured_facts_never_nominal_rate_derived("synthetic.bad", bad)


def test_structural_gate_ignores_variable_names_and_allowlist_comments() -> None:
    """Comments, renames, or a friendly variable name cannot smuggle a derivation past."""
    for bad in (
        "# duration_ts is an authenticated measured fact, safe to scale\n"
        'scaled = facts["duration_ts"] / nominal_frame_ticks\n',
        'measured_container_fact = facts["duration_ts"] * 25\n',
        'AUTHENTICATED_MEASURED_FACT = facts["duration_ts"] - origin\n',
    ):
        with pytest.raises(AssertionError):
            _assert_measured_facts_never_nominal_rate_derived("synthetic.disguised", bad)


def test_structural_gate_rejects_multi_step_aliased_nominal_rate_derivation() -> None:
    """R-184-01: an alias declared on one line cannot launder a derivation.

    The previous line-oriented scanner only inspected lines that literally named a
    measured fact, so splitting the read and the arithmetic across two statements
    (or two variables) bypassed it.  These are the bypass shapes the review finding
    recorded, plus the nearest aliasing variants.
    """
    for bad in (
        # The reported minimal bypass: fact read on one line, scaling on the next.
        'measured_duration = facts["duration_ts"]\n'
        'source_endpoint = measured_duration * fps\n',
        # A two-hop alias chain with a division instead of a multiplication.
        'measured_duration = facts["duration_ts"]\n'
        'frame_count = measured_duration // frame_step\n'
        'source_endpoint = frame_count * nominal_rate\n',
        # Tail-duration aliased, then divided by a nominal rate.
        'tail = facts["tail_duration_ticks"]\n'
        'scaled = tail / computed_frame_rate\n',
        # A measured collection length scaled by a declared rate.
        'offsets = facts["composition_offsets"]\n'
        'window = len(offsets) * declared_rate\n',
        # Alias hidden behind an annotation, then scaled.
        'measured: int = facts["duration_ts"]\n'
        'endpoint = measured * frames_per_second\n',
        # Stashing the fact in a container must not launder the derivation either.
        'bundle = {"v": facts["duration_ts"]}\n'
        'endpoint = bundle["v"] * fps\n',
        'measured_duration = facts["duration_ts"]\n'
        'bundle = {"v": measured_duration}\n'
        'endpoint = bundle["v"] * fps\n',
        # Iterating the closed field-set must not launder the keys either.
        'for key in _V2_ADDITIONAL_EVIDENCE_FIELDS:\n'
        '    source_endpoint = facts[key] * fps\n',
        'KEYS = frozenset({"duration_ts"})\n'
        'for key in KEYS:\n'
        '    source_endpoint = facts[key] * fps\n',
    ):
        with pytest.raises(AssertionError):
            _assert_measured_facts_never_nominal_rate_derived("synthetic.aliased", bad)


def test_structural_gate_is_fail_closed_on_unrecognized_fact_key_roles() -> None:
    """A fact key moved into a recognised-only-at-runtime role must refuse."""
    for bad in (
        # Dynamic key construction: the literal leaves the recognised read role.
        'key = "duration_ts"\n'
        'measured_duration = facts[key]\n'
        'source_endpoint = measured_duration * fps\n',
        # getattr() can reach the same measured value without a subscript.
        'measured_duration = getattr(facts, "duration_ts")\n'
        'source_endpoint = measured_duration * fps\n',
        # Concatenated fact key: fail closed rather than guess the value.
        'measured_duration = facts["duration_" + "ts"]\n'
        'source_endpoint = measured_duration * fps\n',
        # An all-caps scalar alias of the key is not a closed field-set declaration.
        'DURATION_KEY = "duration_ts"\n'
        'source_endpoint = facts[DURATION_KEY] * fps\n',
        # Unparseable source is never assumed safe.
        'def broken(:\n',
    ):
        with pytest.raises(AssertionError):
            _assert_measured_facts_never_nominal_rate_derived("synthetic.dynamic", bad)


def test_structural_gate_allows_parser_reads_and_closed_evidence_serialization() -> None:
    """Reads, validation arithmetic between measured facts, and serialization pass.

    This is the legitimate shape the production v2 binder uses: parser-result reads
    are aliased, two measured facts are compared, and the sealed values are copied
    into a closed evidence dict / receipt.  The gate must not fire on it, or it is
    merely a blanket arithmetic ban rather than a nominal-rate provenance control.
    """
    good = (
        'def bind(measured, evidence):\n'
        '    duration = measured.get("duration_ts")\n'
        '    offsets = measured.get("composition_offsets")\n'
        '    tail = measured.get("tail_duration_ticks")\n'
        '    pts = measured.get("pts_ticks")\n'
        '    consistency = measured.get("duration_consistency")\n'
        '    expected = "MATCH" if duration == pts[-1] + tail else "MISMATCH"\n'
        '    body = {"duration_ts": duration, "tail_duration_ticks": tail,\n'
        '            "composition_offsets": list(offsets),\n'
        '            "duration_consistency": consistency}\n'
        '    receipt = Evidence(duration_ts=duration, stream_handler="mp4")\n'
        '    return body, receipt\n'
    )
    _assert_measured_facts_never_nominal_rate_derived("synthetic.good", good)


def _capture_into(tmp_path: Path, blob: bytes, *, name: str):
    """Capture ``blob`` into its own store and return ``(store, snapshot)``."""
    source = tmp_path / f"{name}.mp4"
    source.write_bytes(blob)
    store = SourceSnapshotStore(
        tmp_path / f"store-{name}", max_source_bytes=64_000, max_store_bytes=256_000,
    )
    snapshot = store.capture(
        source,
        expected_sha256=hashlib.sha256(blob).hexdigest(),
        authorization_id=f"authorization:{name}",
        source_revision_id=f"revision:{name}",
    )
    return store, snapshot


def test_v2_refuses_aliased_or_untrusted_measured_fact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A duck-typed/aliased measured value is not an authenticated measured fact."""

    class AliasedInt(int):
        pass

    blob = _vfr_bytes()
    store, snapshot = _capture_into(tmp_path, blob, name="aliased-fact")
    import gate3.container as container_module

    real_parse = container_module.parse_iso_bmff_timing_bytes

    def fake_parse(raw, *, selected_stream_index=None):
        measured = real_parse(raw, selected_stream_index=selected_stream_index)
        measured["duration_ts"] = AliasedInt(measured["duration_ts"])
        return measured

    monkeypatch.setattr(container_module, "parse_iso_bmff_timing_bytes", fake_parse)

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_TEMPORAL_FACTS_INVALID"):
        store.bind_temporal_authority_v2(
            snapshot,
            selected_stream_index=0,
            declared_vfr=True,
            declared_reordering=False,
        )


def test_v2_binding_detects_retained_byte_mutation_after_sealing(tmp_path: Path) -> None:
    """Re-verification replays against retained bytes, not against the receipt."""
    blob = _vfr_bytes()
    store, snapshot = _capture_into(tmp_path, blob, name="mutated-bytes")
    evidence = store.bind_temporal_authority_v2(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
    ).as_evidence()

    retained = snapshot.snapshot_path
    retained.chmod(stat.S_IRUSR | stat.S_IWUSR)
    retained.write_bytes(retained.read_bytes()[:-6])
    retained.chmod(stat.S_IRUSR)

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        store.verify_temporal_authority(snapshot, json.loads(json.dumps(evidence)))


def test_declared_nominal_rate_cannot_rewrite_measured_positions(tmp_path: Path) -> None:
    _, source, _ = _capture(tmp_path, _vfr_bytes())
    facts = parse_iso_bmff_timing(source)

    record = _refine_measured(source, facts, 400, 600, declared_rate=25)

    assert record["evidence_class"] == "MEASURED"
    assert (record["start_ticks"], record["end_ticks"]) == (400, 600)
    assert record["time_base"] == {"num": 1, "den": VFR_TIMESCALE}
    binding_entry = next(
        item for item in record["validation_results"] if item.get("check") == BINDING_CHECK
    )
    assert tuple(binding_entry["pts_ticks"]) == tuple(facts["pts_ticks"])


# ---------------------------------------------------------------------------
# 4. Semantic candidates are never promoted to source-exact evidence.
# ---------------------------------------------------------------------------


def test_semantic_candidate_evidence_stays_matched_and_non_binding(tmp_path: Path) -> None:
    _, source, _ = _capture(tmp_path, _vfr_bytes())
    facts = parse_iso_bmff_timing(source)
    request = RefinementRequest(
        request_id="request-semantic",
        candidate_assertion_ref="assertion-semantic",
        source_revision_id="revision:generated-vfr.mp4",
        source_locator=str(source),
        expected_source_sha256=facts["source_bytes_sha256"],
        selected_stream_index=facts["stream_index"],
        requested_start_pts=0,
        requested_end_pts=1,
        producer_attempt_id="attempt-1",
        idempotency_key="idempotency-semantic",
        expected_timebase=None,
    )

    candidate = refinement_adapter._candidate_record(
        _refinement_hit(source, facts), request, facts["source_bytes_sha256"],
    )

    assert candidate["time_domain"] == "semantic_seconds"
    assert candidate["precision"] == "semantic-window"
    assert candidate["evidence_class"] == "MATCHED"
    assert candidate["binding_eligible"] is False
    assert candidate["refinement_eligibility"] == "NOT_ELIGIBLE"
    assert candidate["start"] == 0 and candidate["end"] == 1
    assert is_binding_eligible(candidate) is False
    assert is_structurally_eligible(candidate) is False


def test_semantic_seconds_cannot_enter_the_measured_binding_domain(tmp_path: Path) -> None:
    _, source, _ = _capture(tmp_path, _vfr_bytes())
    facts = parse_iso_bmff_timing(source)
    table = PtsTable(TimeBase(1, facts["media_timescale"]), tuple(facts["pts_ticks"]))
    # 0.5 semantic seconds in the source's 1/1000 timebase.
    semantic_second_tick = 500
    assert semantic_second_tick not in table.ticks

    blocked = refine(
        table,
        (400, 600),
        attempt_id="attempt-1",
        tool_identity={"tool": "synthetic-temporal-safety"},
        time_domain="semantic_seconds",
        precision="semantic-window",
        source_revision_id="revision:generated-vfr.mp4",
        source_content_digest=facts["source_bytes_sha256"],
        stream_index=facts["stream_index"],
        container_path=str(source),
        request_identity=_request_identity(source, facts, 400, 600),
    )
    assert blocked == {"blocked": "UNSUPPORTED_BINDING_DOMAIN", "time_domain": "semantic_seconds"}

    with pytest.raises(RefinementRefusal, match="requested start endpoint is not a measured source PTS"):
        refine_retrieval_candidate(
            _refinement_hit(source, facts),
            source_revision_id="revision:generated-vfr.mp4",
            requested_pts=(semantic_second_tick, 600),
            attempt_id="attempt-1",
        )


def test_measured_evidence_cannot_be_relabeled_to_a_weaker_class(tmp_path: Path) -> None:
    _, source, _ = _capture(tmp_path, _vfr_bytes())
    facts = parse_iso_bmff_timing(source)
    measured_record = _refine_measured(source, facts, 400, 600)
    assert measured_record["evidence_class"] == "MEASURED"
    assert is_structurally_eligible(measured_record) is True
    assert is_binding_eligible(measured_record) is True

    for weaker_class in ("MATCHED", "VISUALLY_OBSERVED", "AUDIO_OBSERVED", "EDITORIAL_INFERENCE"):
        relabeled = json.loads(json.dumps(measured_record))
        relabeled["evidence_class"] = weaker_class
        relabeled["evidence_digest"] = gate3_authority.evidence_digest(
            gate3_authority.RECORD_KIND_REFINEMENT, relabeled,
        )
        assert not is_structurally_eligible(relabeled), weaker_class
        assert not is_binding_eligible(relabeled), weaker_class


def test_service_refuses_a_non_measured_authoritative_evidence_class() -> None:
    service_source = inspect.getsource(real_source_service)

    # D6 no-upgrade gate: the authoritative class must be exactly MEASURED, with
    # an exact-type check so an equal-comparing str subclass cannot smuggle a
    # weaker class past the gate.
    assert "AUTHORITATIVE_REFINEMENT_EVIDENCE_CLASS_MISMATCH" in service_source
    assert "type(authoritative_evidence_class) is not str" in service_source
    assert 'authoritative_evidence_class != "MEASURED"' in service_source


# ---------------------------------------------------------------------------
# 5. Tampered timing boxes / mutated retained bytes must refuse.
# ---------------------------------------------------------------------------


def test_truncated_ctts_box_refuses_temporal_measurement(tmp_path: Path) -> None:
    truncated = _truncate_leaf(
        _vfr_bytes(deltas=(40, 40, 80, 80), ctts_offsets=(0, 80, -40, -40)), b"ctts", remove=4,
    )
    store, _, snapshot = _capture(tmp_path, truncated, name="truncated-ctts.mp4")

    with pytest.raises(
        SourceSnapshotError, match="SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED",
    ) as excinfo:
        store.bind_temporal_authority(
            snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=True,
        )
    assert isinstance(excinfo.value.__cause__, ValueError)


def test_stts_entry_count_beyond_its_box_refuses_temporal_measurement(tmp_path: Path) -> None:
    store, _, snapshot = _capture(
        tmp_path, _inflate_stts_entry_count(_vfr_bytes()), name="inflated-stts.mp4",
    )

    with pytest.raises(
        SourceSnapshotError, match="SNAPSHOT_TEMPORAL_MEASUREMENT_REFUSED",
    ) as excinfo:
        store.bind_temporal_authority(
            snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
        )
    assert isinstance(excinfo.value.__cause__, struct.error)


def test_duplicate_decode_timestamps_refuse_binding(tmp_path: Path) -> None:
    store, _, snapshot = _capture(
        tmp_path,
        build_mp4(media_timescale=25, sample_deltas=(5, 0, 5, 5)),
        name="duplicate-decode-timestamps.mp4",
    )

    # A zero sample delta yields two frames on the same decode timestamp; the
    # measured facts are structurally valid but not a legal decode timeline.
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DECODE_TIMESTAMPS_INVALID"):
        store.bind_temporal_authority(
            snapshot, selected_stream_index=0, declared_vfr=False, declared_reordering=False,
        )


def test_timebase_mutation_in_retained_snapshot_refuses_verify_and_bind(tmp_path: Path) -> None:
    store, source, snapshot = _capture(tmp_path, _vfr_bytes())
    binding = store.bind_temporal_authority(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
    )
    assert (binding.timebase_num, binding.timebase_den) == (1, VFR_TIMESCALE)

    snapshot_path = snapshot.snapshot_path
    original_mode = stat.S_IMODE(snapshot_path.stat().st_mode)
    os.chmod(snapshot_path, 0o600)
    try:
        raw = bytearray(snapshot_path.read_bytes())
        mdhd_start = raw.index(b"mdhd") - 4
        # version/flags (4) + creation_time (4) + modification_time (4) then timescale.
        timescale_offset = mdhd_start + 8 + 4 + 8
        assert struct.unpack_from(">I", raw, timescale_offset)[0] == VFR_TIMESCALE
        struct.pack_into(">I", raw, timescale_offset, 900)
        snapshot_path.write_bytes(bytes(raw))
    finally:
        os.chmod(snapshot_path, original_mode)

    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        store.verify(snapshot)
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        store.bind_temporal_authority(
            snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
        )
    with pytest.raises(SourceSnapshotError, match="SNAPSHOT_DIGEST_MISMATCH"):
        store.verify_temporal_authority(snapshot, binding.as_evidence())


def test_mutated_evidence_timebase_refuses_temporal_verification(tmp_path: Path) -> None:
    store, _, snapshot = _capture(tmp_path, _vfr_bytes())
    binding = store.bind_temporal_authority(
        snapshot, selected_stream_index=0, declared_vfr=True, declared_reordering=False,
    )
    evidence = dict(binding.as_evidence())
    evidence["timebase"] = {"num": 1, "den": 900}

    with pytest.raises(
        SourceSnapshotError, match="SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH",
    ):
        store.verify_temporal_authority(snapshot, evidence)
