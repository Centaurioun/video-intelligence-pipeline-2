"""Deterministic source-native refinement. Only Gate-3 C2 outputs can bind.

FR-01: a binding-eligible C2 record derives its source coordinates, digest and selected
stream from named container bytes (re-measured inside this module) or from a verified
persisted measurement artifact.  A caller-provided table/digest/stream alone can never
create authority.
FR-02: ``source_frame`` coordinates are 0-based retained presentation-order ordinals
(half-open in ordinal space), separate from ``source_pts`` ticks; the selected video
stream is explicit; unsupported ``ctts``/``elst``/ambiguous-track shapes fail closed;
the T8 DTS/reorder predicate is enforced on presentation-ordinal claims.
FR-03: a derived tail carries its ``extent_state``, derivation and measurement reference,
and cannot bind without admissible measured end-boundary evidence.

Binding authority is split (owner ruling on FX-2, ledger sec.16):

* ``is_structurally_eligible`` is a **shape-only** predicate.  A record that satisfies it
  has declared a self-consistent C2 evidence shape; that is **not** Gate-3 binding
  authority and no consumer may grant binding from it.
* ``is_binding_eligible`` is the **authoritative** predicate.  It additionally requires the
  FR-01 evidence: the C2 entry must name the source bytes (a container path) or a persisted
  byte-bound measurement artifact, and the declaration is re-measured and matched against
  the named bytes.  A hand-written record whose digest, stream or enumeration the named
  bytes contradict is refused.
"""
from __future__ import annotations
import hashlib,json,pathlib
from collections.abc import Mapping
from gate3 import authority
from gate3.authority import RECORD_KIND_REFINEMENT
from gate3.container import _resolved_byte_source_path, verified_measurement_artifact
from gate3.ordinal import FrameOrdinalBasis, dts_evidence_required
from gate3.pts import PtsTable
from gate3.temporal import PRECISION_TOKENS, classify_vfr, detect_discontinuity

BINDING_DOMAINS=("source_pts","source_frame")
A3_PRECISION_FOR_DOMAIN={"source_pts":"source-pts","source_frame":"source-frame"}
TAIL_DERIVATION="pts_start_tick->duration_ts_tail_end"
PTS_DERIVATION="pts_start_tick->pts_end_tick"
ORDINAL_DERIVATION="retained_presentation_ordinal_start->ordinal_end_half_open"
BINDING_CHECK="C2_named_byte_binding"
T8_CHECK="T8_dts_reorder_evidence"
TAIL_REFERENCE_CHECK="C2_tail_measurement_reference"
BYTE_BINDING_DERIVATIONS=("named_bytes_remeasured","persisted_measurement_artifact")
TAIL_EXTENT_STATES=("DERIVED_NOT_OBSERVED",)
# Inside the C2 entry: the byte source that entry's declaration must be re-measured against.
BYTE_AUTHORITY_FIELD="byte_authority"

def _exact_int(value):
    """Type-aware integer identity (MAJOR-B/FR-10); ``bool`` is never an integer here."""
    return isinstance(value,int) and not isinstance(value,bool)

def _container_facts_binding(facts):
    return {"nb_frames":facts.get("nb_frames"),"duration_ts":facts.get("duration_ts"),
            "duration_consistency":facts.get("duration_consistency")}

def _resolve_byte_authority(*,table,source_content_digest,stream_index,container_path,
                            measurement_artifact,selected_stream_index,ordinal_space=False,
                            measurement_artifact_path=None):
    """Return ``(facts, mode)`` bound to named bytes, or ``(None, blocked_record)``.

    ``facts`` always names the measured bytes by digest and enumerates the retained
    presentation PTS actually measured from them; the caller's table is checked against
    that enumeration, so a forged table cannot ride on an honest digest.
    """
    if container_path:
        from gate3.container import parse_iso_bmff_timing
        try:
            measured=parse_iso_bmff_timing(container_path,selected_stream_index=selected_stream_index)
        except (OSError,ValueError) as exc:
            return None,{"blocked":"CONTAINER_UNMEASURABLE","detail":str(exc)}
        facts=measured;mode="named_bytes_remeasured"
    elif measurement_artifact_path:
        try:
            artifact=json.loads(pathlib.Path(measurement_artifact_path).read_text())
        except (OSError,ValueError) as exc:
            return None,{"blocked":"PERSISTED_MEASUREMENT_ARTIFACT_UNREADABLE","detail":str(exc)}
        # FR-01: admissibility requires that the artifact resolves its declared bytes.
        facts,reason=verified_measurement_artifact(artifact,require_resolved_bytes=True)
        if facts is None:return None,{"blocked":reason}
        mode="persisted_measurement_artifact"
    elif measurement_artifact is not None:
        facts,reason=verified_measurement_artifact(measurement_artifact,require_resolved_bytes=True)
        if facts is None:return None,{"blocked":reason}
        mode="persisted_measurement_artifact"
    else:
        return None,{"blocked":"BYTE_BOUND_SOURCE_AUTHORITY_REQUIRED"}
    if not source_content_digest or facts["source_bytes_sha256"]!=source_content_digest:
        return None,{"blocked":"SOURCE_DIGEST_DOES_NOT_MATCH_NAMED_BYTES",
                     "declared":source_content_digest,"measured":facts["source_bytes_sha256"]}
    if facts["stream_index"]!=stream_index:
        # Ordered before the type guard on purpose: a coercion that names a DIFFERENT stream is
        # reported as the mismatch it is, so the permanent cross-stream guards in
        # tests/gate3/test_gen2_r8_stream_index_type_authority.py keep their named reason.
        return None,{"blocked":"STREAM_INDEX_DOES_NOT_MATCH_NAMED_BYTES",
                     "declared":stream_index,"measured":facts["stream_index"]}
    # MAJOR-B: a numerically-coincident bool/float is not an exact integer stream identity.
    if not _exact_int(stream_index) or stream_index<0:
        return None,{"blocked":"STREAM_INDEX_NOT_A_NON_NEGATIVE_INTEGER","declared":stream_index}
    if tuple(table.ticks)!=tuple(facts["pts_ticks"]):
        # A source_pts table may name a contiguous sub-sequence of the measured presentation
        # enumeration (still byte-derived); a source_frame ordinal basis must cover the whole
        # retained enumeration because ordinals are only defined over it.
        measured=list(facts["pts_ticks"]);declared=list(table.ticks);n=len(declared)
        contiguous=bool(n) and any(declared==measured[i:i+n] for i in range(len(measured)-n+1))
        if ordinal_space or not contiguous:
            return None,{"blocked":"ENUMERATION_DOES_NOT_MATCH_NAMED_BYTES",
                         "declared":tuple(table.ticks),"measured":tuple(facts["pts_ticks"])}
    declared_num=getattr(table.time_base,"num",None)
    declared_den=getattr(table.time_base,"den",None)
    if (not _exact_int(declared_num) or declared_num!=1
            or not _exact_int(declared_den) or not _exact_int(facts["media_timescale"])
            or declared_den!=facts["media_timescale"]):
        return None,{"blocked":"TIME_BASE_DOES_NOT_MATCH_NAMED_BYTES",
                     "declared_num":declared_num,"declared_den":declared_den,
                     "measured_num":1,"measured_den":facts["media_timescale"]}
    origin=facts.get("presentation_origin_ticks")
    if origin is not None and (not _exact_int(origin) or origin!=0):
        return None,{"blocked":"EDIT_LIST_ORIGIN_NOT_APPLIED",
                     "presentation_origin_ticks":origin}
    return facts,mode

def _tail_state(table,facts,*,compare_end):
    from gate3.temporal import tail_end
    container_facts=_container_facts_binding(facts)
    if container_facts["nb_frames"] is None or container_facts["duration_ts"] is None:
        return False,{"blocked":"TAIL_MEASUREMENT_MISSING_CONTAINER_FACTS"}
    try:
        computed=tail_end(table,container_facts=container_facts)
    except ValueError as exc:
        return False,{"blocked":"TAIL_FACTS_INCONSISTENT","detail":str(exc)}
    if not computed.binding_eligible:
        return False,{"blocked":"TAIL_NOT_BINDING_ELIGIBLE","extent_state":computed.extent_state}
    if compare_end is not None and computed.end_ticks!=compare_end:
        return False,{"blocked":"TAIL_RECOMPUTED_END_DIFFERS","requested":compare_end,"recomputed":computed.end_ticks}
    return True,{"derivation":computed.derivation,"extent_state":computed.extent_state,
                 "measured_source_digest":facts["source_bytes_sha256"],
                 "tail_end_ticks":computed.end_ticks,"container_facts":container_facts}

def recompute_tail(table:PtsTable,end:int|None,*,source_content_digest:str|None,stream_index:int,
                   container_path:str|None=None,measurement_artifact:dict|None=None,
                   selected_stream_index:int|None=None,measurement_artifact_path:str|None=None):
    """Public tail recomputation: named-bytes-bound or verified-artifact-bound only."""
    facts,_mode=_resolve_byte_authority(table=table,source_content_digest=source_content_digest,
                                        stream_index=stream_index,container_path=container_path,
                                        measurement_artifact=measurement_artifact,
                                        selected_stream_index=selected_stream_index,
                                        measurement_artifact_path=measurement_artifact_path)
    if facts is None:
        return False,_mode
    return _tail_state(table,facts,compare_end=end)

def _binding_entry(record):
    # R-13: FR-11 plans deep-freeze their pinned records (MappingProxyType/tuple), so every
    # predicate here must accept any Mapping/Sequence, never a concrete dict/list.
    results=record.get("validation_results")
    if not isinstance(results,(list,tuple)):return None
    for entry in results:
        if isinstance(entry,Mapping) and entry.get("check")==BINDING_CHECK:return entry
    return None

def _request_identity_failure(request_identity,attempt_id):
    if request_identity is None:return "REFINEMENT_REQUEST_IDENTITY_REQUIRED"
    required_identity={"request_id","candidate_assertion_ref","producer_attempt_id","idempotency_key","request_digest","request"}
    if (not isinstance(request_identity,Mapping) or set(request_identity)!=required_identity
            or any(not isinstance(request_identity.get(key),str) or not request_identity.get(key)
                   for key in required_identity-{"request"}) or not isinstance(request_identity.get("request"),Mapping)):
        return "REFINEMENT_REQUEST_IDENTITY_INVALID"
    request=request_identity["request"]
    required_request={"request_id","candidate_assertion_ref","source_revision_id","source_locator",
                      "expected_source_sha256","selected_stream_index","requested_start_pts",
                      "requested_end_pts","producer_attempt_id","idempotency_key","expected_timebase"}
    if set(request)!=required_request:
        return "REFINEMENT_REQUEST_IDENTITY_INVALID"
    if any(not isinstance(request.get(key),str) or not request.get(key)
           for key in ("request_id","candidate_assertion_ref","source_revision_id","source_locator",
                       "expected_source_sha256","producer_attempt_id","idempotency_key")):
        return "REFINEMENT_REQUEST_IDENTITY_INVALID"
    if (not isinstance(request.get("selected_stream_index"),int)
            or isinstance(request.get("selected_stream_index"),bool)
            or request["selected_stream_index"]<0
            or not _exact_int(request.get("requested_start_pts"))
            or not _exact_int(request.get("requested_end_pts"))
            or request["requested_end_pts"]<=request["requested_start_pts"]):
        return "REFINEMENT_REQUEST_IDENTITY_INVALID"
    if (request_identity.get("request_id")!=request.get("request_id")
            or request_identity.get("candidate_assertion_ref")!=request.get("candidate_assertion_ref")
            or request_identity.get("producer_attempt_id")!=request.get("producer_attempt_id")
            or request_identity.get("idempotency_key")!=request.get("idempotency_key")):
        return "REFINEMENT_REQUEST_IDENTITY_INVALID"
    if request_identity.get("producer_attempt_id")!=attempt_id:
        return "REFINEMENT_REQUEST_ATTEMPT_MISMATCH"
    request_digest=request_identity.get("request_digest")
    if len(request_digest)!=64 or any(ch not in "0123456789abcdef" for ch in request_digest):
        return "REFINEMENT_REQUEST_DIGEST_INVALID"
    try:
        canonical_request=authority.canonical_json(dict(request))
    except (TypeError,ValueError):
        return "REFINEMENT_REQUEST_IDENTITY_INVALID"
    if hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()!=request_digest:
        return "REFINEMENT_REQUEST_DIGEST_INVALID"
    return None

def _request_identity_matches_c2(request_identity,*,source_revision_id,source_digest,stream_index,
                                 start,end,time_base,time_domain,container_path):
    request=request_identity.get("request") if isinstance(request_identity,Mapping) else None
    if not isinstance(request,Mapping):return False
    if (time_domain!="source_pts" or request.get("source_revision_id")!=source_revision_id
            or request.get("expected_source_sha256")!=source_digest
            or request.get("selected_stream_index")!=stream_index
            or request.get("requested_start_pts")!=start
            or request.get("requested_end_pts")!=end):
        return False
    if container_path is not None and request.get("source_locator")!=str(container_path):return False
    if not isinstance(time_base,Mapping):return False
    actual_num=time_base.get("num");actual_den=time_base.get("den")
    if (not _exact_int(actual_num) or not _exact_int(actual_den)
            or actual_num<=0 or actual_den<=0):return False
    expected=request.get("expected_timebase")
    if expected is not None:
        if (not isinstance(expected,(list,tuple)) or len(expected)!=2
                or not _exact_int(expected[0]) or not _exact_int(expected[1])
                or expected[0]<=0 or expected[1]<=0):return False
        if expected[0]*actual_den!=actual_num*expected[1]:return False
    return True

def _binding_covers(record):
    entry=_binding_entry(record)
    if entry is None:return False
    if _request_identity_failure(entry.get("request_identity"),record.get("attempt_id")):return False
    if not _request_identity_matches_c2(entry["request_identity"],
                                        source_revision_id=record.get("source_revision_id"),
                                        source_digest=entry.get("source_bytes_sha256"),
                                        stream_index=entry.get("measured_stream_index"),
                                        start=record.get("start_ticks"),end=record.get("end_ticks"),
                                        time_base=record.get("time_base"),
                                        time_domain=record.get("time_domain"),
                                        container_path=(_named_byte_source(entry) or {}).get("container_path")):
        return False
    if entry.get("derivation") not in BYTE_BINDING_DERIVATIONS:return False
    if entry.get("source_bytes_sha256")!=record.get("source_content_digest"):return False
    # MAJOR-B: the selected stream identity is an exact integer on both sides (fx08 discipline:
    # whatever the producer admits with binding authority must satisfy the frozen schema).
    if not _exact_int(record.get("stream_index")) or not _exact_int(entry.get("measured_stream_index")):
        return False
    if entry.get("measured_stream_index")!=record.get("stream_index"):return False
    enumerated=entry.get("pts_ticks")
    if not isinstance(enumerated,(list,tuple)) or not enumerated:return False
    if any(not _exact_int(t) for t in enumerated):return False
    if any(b<a for a,b in zip(enumerated,enumerated[1:])):return False
    if not _exact_int(entry.get("nb_frames")) or entry.get("nb_frames")!=len(enumerated):return False
    # FR-02/MAJOR-B: endpoints are exact integers in every domain; a bool/float is not a
    # coordinate, even when it compares numerically equal to a retained tick or ordinal.
    start=record.get("start_ticks");end=record.get("end_ticks")
    if not _exact_int(start) or not _exact_int(end):return False
    domain=record.get("time_domain")
    if domain=="source_pts":
        if start not in enumerated:return False
        if not record.get("end_is_stream_tail") and end not in enumerated:return False
    elif domain=="source_frame":
        # BLOCKER-3 / T2: a source_frame endpoint is a 0-based RETAINED presentation ordinal, so
        # the interval is bounded by the retained enumeration the named bytes measured -- not by
        # the record's own claim.  `refine()` enforces this at production time; a record can be
        # rewritten afterwards, so the authoritative predicate must re-derive it here.
        retained=len(enumerated)
        if not (0<=start<end<=retained):return False
        if record.get("end_is_stream_tail") and end!=retained:return False
    else:
        return False
    return True

def _dts_evidence_ok(record):
    """STRUCTURAL T8 self-consistency: re-derive the requirement from the entry's declared facts.

    The record's own ``dts_evidence_required`` flag is never the trigger (BLOCKER-2).  Absent or
    ill-typed reorder facts cannot establish that no DTS evidence is required, so they fail
    closed rather than defaulting to "not required".
    """
    entry=_binding_entry(record)
    if entry is None:return False
    has_b_frames=entry.get("has_b_frames");pts_equals_dts=entry.get("pts_equals_dts")
    if not _exact_int(has_b_frames) or not isinstance(pts_equals_dts,bool):
        required=True
    else:
        required=dts_evidence_required(has_b_frames=has_b_frames,pts_equals_dts=pts_equals_dts)
    if required:
        dts=entry.get("dts_ticks")
        if not isinstance(dts,(list,tuple)) or not dts:return False
        if any(not _exact_int(t) for t in dts):return False
    return True

def _tail_evidence_ok(record):
    if record.get("method",{}).get("derivation")!=TAIL_DERIVATION:return False
    if record.get("extent_state") not in TAIL_EXTENT_STATES:return False
    reference=record.get("tail_measurement_ref")
    if not isinstance(reference,str) or not reference:return False
    uncertainty=record.get("uncertainty")
    if not isinstance(uncertainty,(list,tuple)):return False
    for item in uncertainty:
        if not isinstance(item,Mapping):continue
        facts=item.get("container_facts")
        if (item.get("measured_source_digest")==record.get("source_content_digest")
                and isinstance(facts,Mapping) and facts.get("duration_consistency")=="MATCH"
                and isinstance(item.get("derivation"),str) and "duration_ts" in item["derivation"]):
            return True
    return False

def is_structurally_eligible(record:dict)->bool:
    """SHAPE ONLY: the record is a self-consistent MEASURED source-native C2 *declaration*.

    This predicate never reads bytes and therefore never establishes Gate-3 binding
    authority: a hand-written record that asserts a digest, stream and enumeration the
    named bytes contradict satisfies it.  It exists so structural/schema consumers can ask
    "is this the right shape?" without implying authority.  Binding decisions must use
    :func:`is_binding_eligible`.
    """
    if not isinstance(record,Mapping):return False
    if not record.get("produced_by_gate3_refinement_attempt"):return False
    if record.get("evidence_class")!="MEASURED":return False
    domain=record.get("time_domain")
    if domain not in BINDING_DOMAINS:return False
    if not _binding_covers(record):return False
    if record.get("end_is_stream_tail") and not _tail_evidence_ok(record):return False
    if domain=="source_frame":
        if not record.get("method",{}).get("retained_enumeration"):return False
        if not isinstance(record.get("frame_ordinal_basis"),Mapping):return False
    # Owner ruling R-6 (Spec §14): the reorder-evidence self-consistency requirement applies in
    # BOTH binding domains.  `_dts_evidence_ok` re-derives the requirement from the entry's own
    # declared facts and refuses absent/ill-typed facts, so it is domain-independent.
    if not _dts_evidence_ok(record):return False
    return True

def _named_byte_source(entry):
    """Return the C2 entry's byte-source reference, or ``None`` when it names no bytes."""
    authority=entry.get(BYTE_AUTHORITY_FIELD)
    return authority if isinstance(authority,Mapping) else None

def _remeasured_facts(entry):
    """Re-measure the byte source the C2 entry names. Returns ``(facts, None)`` or ``(None, reason)``.

    This is the FR-01 authority step that ``is_structurally_eligible`` deliberately omits: an
    entry that merely *declares* a digest cannot bind, because the declared digest, stream and
    enumeration are checked against bytes read from disk (or a persisted, verified
    measurement artifact) at predicate time.
    """
    authority=_named_byte_source(entry)
    if authority is None:return None,"BINDING_ENTRY_NAMES_NO_BYTE_SOURCE"
    derivation=entry.get("derivation")
    if derivation not in BYTE_BINDING_DERIVATIONS:return None,"BINDING_DERIVATION_NOT_BYTE_BOUND"
    if derivation=="named_bytes_remeasured":
        path=authority.get("container_path")
        if not isinstance(path,str) or not path:return None,"BINDING_ENTRY_NAMES_NO_CONTAINER_PATH"
        if not pathlib.Path(path).is_file():return None,"NAMED_BYTES_NOT_PRESENT"
        from gate3.container import parse_iso_bmff_timing
        try:
            facts=parse_iso_bmff_timing(path,selected_stream_index=authority.get("selected_stream_index"))
        except (OSError,ValueError) as exc:
            return None,f"NAMED_BYTES_UNMEASURABLE:{exc}"
        return facts,None
    path=authority.get("measurement_artifact_path")
    if not isinstance(path,str) or not path:return None,"BINDING_ENTRY_NAMES_NO_PERSISTED_ARTIFACT_PATH"
    if not pathlib.Path(path).is_file():return None,"PERSISTED_MEASUREMENT_ARTIFACT_NOT_PRESENT"
    try:
        artifact=json.loads(pathlib.Path(path).read_text())
    except (OSError,ValueError) as exc:
        return None,f"PERSISTED_MEASUREMENT_ARTIFACT_UNREADABLE:{exc}"
    # FR-01: the persisted artifact must resolve its declared bytes; a digest naming no bytes is
    # a caller-provided table and can never create binding authority.
    facts,reason=verified_measurement_artifact(artifact,require_resolved_bytes=True)
    if facts is None:return None,reason
    # Preserve the artifact resolver's authoritative path so the request locator can be
    # cross-bound to the same bytes' source, not just to their matching digest.
    resolved_source_path=_resolved_byte_source_path(artifact,facts["source_bytes_sha256"])
    if resolved_source_path is None:return None,"MEASUREMENT_ARTIFACT_DECLARED_BYTES_NOT_RESOLVED"
    facts["resolved_source_path"]=resolved_source_path
    return facts,None

def _byte_authority_covers(record,entry)->bool:
    """True only when the entry's declaration survives re-measurement of its named byte source."""
    facts,_reason=_remeasured_facts(entry)
    if facts is None:return False
    digest=record.get("source_content_digest")
    if not isinstance(digest,str) or not digest:return False
    if facts["source_bytes_sha256"]!=digest:return False
    if entry.get("source_bytes_sha256")!=digest:return False
    snapshot_evidence=entry.get("snapshot_evidence")
    if snapshot_evidence is not None:
        try:
            from vip_fvs.source_snapshot import verify_snapshot_evidence
            verify_snapshot_evidence(snapshot_evidence)
            named=_named_byte_source(entry) or {}
            if (pathlib.Path(named.get("container_path", "")).resolve(strict=True)
                    != pathlib.Path(snapshot_evidence["snapshot_path"]).resolve(strict=True)
                    or snapshot_evidence.get("snapshot_sha256")!=digest):
                return False
        except (OSError, RuntimeError, ValueError, KeyError, TypeError):
            return False
    if entry.get("derivation")=="persisted_measurement_artifact":
        request_identity=entry.get("request_identity")
        request=request_identity.get("request") if isinstance(request_identity,Mapping) else None
        source_locator=request.get("source_locator") if isinstance(request,Mapping) else None
        resolved_source_path=facts.get("resolved_source_path")
        if not isinstance(source_locator,str) or not source_locator or not isinstance(resolved_source_path,str):
            return False
        try:
            if (pathlib.Path(source_locator).resolve(strict=True)
                    !=pathlib.Path(resolved_source_path).resolve(strict=True)):
                return False
        except (OSError,RuntimeError,ValueError):
            return False
    stream=record.get("stream_index")
    if not _exact_int(stream) or not _exact_int(facts.get("stream_index")):return False
    if facts["stream_index"]!=stream:return False
    if not _exact_int(entry.get("measured_stream_index")):return False
    if entry.get("measured_stream_index")!=stream:return False
    # The declared enumeration must BE the enumeration the named bytes retain (FR-01/FR-02).
    if tuple(entry.get("pts_ticks") or ())!=tuple(facts["pts_ticks"]):return False
    declared_timescale=entry.get("media_timescale")
    if declared_timescale is not None:
        if not _exact_int(declared_timescale):return False
        if declared_timescale!=facts["media_timescale"]:return False
    time_base=record.get("time_base")
    if not isinstance(time_base,Mapping):return False
    num=time_base.get("num");den=time_base.get("den")
    if not _exact_int(num) or not _exact_int(den):return False
    if num!=1 or den!=facts["media_timescale"]:return False
    # BLOCKER-2 / frozen T8: re-derive the DTS requirement from the MEASURED bytes, never from
    # the record's or the entry's own `dts_evidence_required` declaration.  A record may not mask
    # a requirement the bytes establish, and decode timestamps are exact integers.
    has_b_frames=facts.get("has_b_frames");pts_equals_dts=facts.get("pts_equals_dts")
    if not _exact_int(has_b_frames) or not isinstance(pts_equals_dts,bool):return False
    measured_required=dts_evidence_required(has_b_frames=has_b_frames,pts_equals_dts=pts_equals_dts)
    declared_dts=entry.get("dts_ticks")
    if declared_dts is not None and (not isinstance(declared_dts,(list,tuple))
                                     or any(not _exact_int(t) for t in declared_dts)):
        return False
    if measured_required:
        if entry.get("dts_evidence_required") is False:return False
        if entry.get("has_b_frames")!=has_b_frames:return False
        if entry.get("pts_equals_dts")!=pts_equals_dts:return False
        # Owner ruling R-6 (Spec §14): T8 is a property of the MEASURED SELECTED STREAM, so the
        # required DTS/reorder evidence must be PRESENT in BOTH binding coordinate domains.
        # This does NOT import source_frame's retained-enumeration requirement into source_pts:
        # only the reorder evidence presence is unified, not the enumeration rule.
        if not declared_dts:return False
        if tuple(declared_dts)!=tuple(facts.get("dts_ticks") or ()):return False
    if record.get("end_is_stream_tail"):
        # `temporal.tail_end` derives the tail end from the measured duration; a tail record may
        # only bind when the named bytes still recompute that end.
        if facts.get("duration_consistency")!="MATCH":return False
        # FR-02/T5 (gen-2 root fix): the tail end is expressed in the RECORD'S OWN typed domain.
        # `source_pts` is a tick domain, so the tail end is the measured duration tick. A
        # `source_frame` record is a 0-based retained presentation ORDINAL domain, so its tail end is
        # the retained-ordinal COUNT -- comparing a tick count against an ordinal was a unit error
        # that made an honest `source_frame` tail structurally eligible but never binding-eligible.
        if record.get("time_domain")=="source_frame":
            if record.get("end_ticks")!=len(entry.get("pts_ticks") or ()):return False
        else:
            if facts.get("duration_ts")!=record.get("end_ticks"):return False
    return True

def is_binding_eligible(record:dict)->bool:
    """AUTHORITATIVE binding eligibility (FR-01/FR-11).

    Structurally eligible **and** byte-bound: the C2 entry must name the source bytes (or a
    persisted measurement artifact) and the declaration is re-measured against them.  This is
    the predicate the plan chain consumes; :func:`is_structurally_eligible` must never be used
    to grant binding.
    """
    if not is_structurally_eligible(record):return False
    entry=_binding_entry(record)
    if entry is None:return False
    return _byte_authority_covers(record,entry)

def _non_binding_record(*,blocked,attempt_id,source_revision_id,source_content_digest,
                        stream_index,time_domain,precision,start,end,extras=None,
                        end_is_stream_tail=False):
    """FR-15 a3 refusal shape: a NAMED, NON-BINDING record rather than a bare blocked dict.

    A downstream verifier must still be able to identify the subject and reach DISAGREE instead
    of raising.  The identity is content-addressed on the declared source digest exactly like the
    binding path, and ``produced_by_gate3_refinement_attempt`` stays false so no predicate can
    mistake a refusal for authority.
    """
    preimage=(f"{attempt_id}:{source_revision_id}:{stream_index}:{start}:{end}:{time_domain}"
              f":{source_content_digest}")
    record={**(extras or {}),"blocked":blocked,
            "refinement_id":f"ref_{hashlib.sha256(preimage.encode()).hexdigest()[:16]}",
            "attempt_id":attempt_id,"source_revision_id":source_revision_id,
            "source_content_digest":source_content_digest,"stream_index":stream_index,
            "time_domain":time_domain,"precision":precision,"start_ticks":start,"end_ticks":end,
            "endpoint_semantics":"half_open","end_is_stream_tail":end_is_stream_tail,
            "evidence_class":"MEASURED","produced_by_gate3_refinement_attempt":False,
            "binding_eligible":False}
    return record

def refine(table:PtsTable,requested:tuple[int,int],*,attempt_id:str,tool_identity:dict,time_domain:str,precision:str,
           retain_enumeration:bool=True,source_revision_id:str,source_content_digest:str,stream_index:int,
           declared_rate=None,container_path:str|None=None,measurement_artifact:dict|None=None,
           selected_stream_index:int|None=None,measurement_artifact_path:str|None=None,
           request_identity:Mapping|None=None,snapshot_evidence:Mapping|None=None)->dict:
    start,end=requested
    if time_domain not in BINDING_DOMAINS:return {"blocked":"UNSUPPORTED_BINDING_DOMAIN","time_domain":time_domain}
    if not isinstance(stream_index,int) or isinstance(stream_index,bool) or stream_index<0:return {"blocked":"STREAM_INDEX_NOT_A_NON_NEGATIVE_INTEGER"}
    if not isinstance(tool_identity,Mapping) or not tool_identity:return {"blocked":"TOOL_IDENTITY_REQUIRED"}
    identity_failure=_request_identity_failure(request_identity,attempt_id)
    if identity_failure:return {"blocked":identity_failure}
    if precision not in PRECISION_TOKENS:return {"blocked":"UNRECOGNISED_PRECISION"}
    if precision!=A3_PRECISION_FOR_DOMAIN[time_domain]:return {"blocked":"PRECISION_NOT_ADMITTED_FOR_DOMAIN"}
    # MAJOR-B: a requested endpoint is an exact integer in both domains.  Checked before any
    # comparison/slice so a float ordinal fails closed deterministically instead of raising
    # `TypeError: slice indices must be integers`, and so two numeric spellings of one source
    # interval cannot mint two binding identities.
    if not _exact_int(start) or not _exact_int(end):
        return _non_binding_record(blocked="REQUESTED_ENDPOINTS_NOT_EXACT_INTEGERS",
                                   attempt_id=attempt_id,source_revision_id=source_revision_id,
                                   source_content_digest=source_content_digest,
                                   stream_index=stream_index,time_domain=time_domain,
                                   precision=precision,start=start,end=end,
                                   extras={"declared_start_ticks":start,"declared_end_ticks":end})
    if end<=start:return {"blocked":"DEGENERATE_INTERVAL"}
    basis=None;ordinal_space=time_domain=="source_frame"
    if ordinal_space:
        basis=FrameOrdinalBasis(table,dedupe_policy="RETENTION",ordering="presentation")
        retained=basis.count()
        if start<0 or end>retained:
            return {"blocked":"SOURCE_FRAME_ORDINAL_OUTSIDE_RETAINED_ENUMERATION",
                    "start_ordinal":start,"end_ordinal":end,"retained_frames":retained}
        end_tail=end==retained
        included_ticks=table.ticks[start:end]
    else:
        if not table.is_boundary_member(start):return {"blocked":"ENDPOINT_NOT_A_PTS_MEMBER"}
        end_tail=not table.is_boundary_member(end)
        included_ticks=table.ticks
    if end_tail and not container_path:return {"blocked":"TAIL_REQUIRES_MEASURED_CONTAINER"}
    facts,mode=_resolve_byte_authority(table=table,source_content_digest=source_content_digest,
                                       stream_index=stream_index,container_path=container_path,
                                       measurement_artifact=measurement_artifact,
                                       selected_stream_index=selected_stream_index,
                                       measurement_artifact_path=measurement_artifact_path,
                                       ordinal_space=ordinal_space)
    if facts is None:
        # FR-01 refusal: the declared source authority does not match the named bytes. Return a NAMED,
        # NON-BINDING record rather than a bare blocked dict, so a downstream verifier can still identify
        # the subject and reach DISAGREE instead of raising (FR-15 a3). `blocked` is preserved for every
        # existing assertion that reads it.
        return _non_binding_record(blocked=mode["blocked"],extras=mode,attempt_id=attempt_id,
                                   source_revision_id=source_revision_id,
                                   source_content_digest=source_content_digest,
                                   stream_index=stream_index,time_domain=time_domain,
                                   precision=precision,start=start,end=end,
                                   end_is_stream_tail=end_tail)
    if not _request_identity_matches_c2(request_identity,
                                        source_revision_id=source_revision_id,
                                        source_digest=facts["source_bytes_sha256"],
                                        stream_index=facts["stream_index"],
                                        start=start,end=end,
                                        time_base={"num":table.time_base.num,"den":table.time_base.den},
                                        time_domain=time_domain,container_path=container_path):
        return {"blocked":"REFINEMENT_REQUEST_C2_MISMATCH"}
    tail_detail=None
    if end_tail:
        ok,tail_detail=_tail_state(table,facts,compare_end=end if not ordinal_space else None)
        if not ok:return tail_detail
    if ordinal_space:
        if len(included_ticks)>=2 and detect_discontinuity(table,included_ticks[0],included_ticks[-1]):
            return {"blocked":"DISCONTINUITY_SPANNED"}
    elif detect_discontinuity(table,start,end):
        return {"blocked":"DISCONTINUITY_SPANNED"}
    vfr,p,vfr_basis,deviation=classify_vfr(table,declared_rate)
    # BLOCKER-4: the refinement identity is content-addressed on the RESOLVED source digest, so
    # records derived over different byte sources with otherwise identical interval spelling can
    # never collide on the FR-11 cross-link identity.
    request_identity_digest=(authority.canonical_json(dict(request_identity)) if request_identity is not None else "")
    digest=hashlib.sha256((f"{attempt_id}:{source_revision_id}:{stream_index}:{start}:{end}:{time_domain}:"
                           f"{facts['source_bytes_sha256']}:{request_identity_digest}").encode()).hexdigest()
    dts_ticks=list(facts.get("dts_ticks") or ())
    composition_offsets=list(facts.get("composition_offsets") or ())
    pts_equals_dts=bool(facts.get("pts_equals_dts",True))
    has_b_frames=int(facts.get("has_b_frames") or 0)
    reorder_required=dts_evidence_required(has_b_frames=has_b_frames,pts_equals_dts=pts_equals_dts)
    binding={"check":BINDING_CHECK,"derivation":mode,"source_bytes_sha256":facts["source_bytes_sha256"],
             "measured_stream_index":facts["stream_index"],"media_timescale":facts["media_timescale"],
             "nb_frames":facts["nb_frames"],"pts_ticks":list(facts["pts_ticks"]),
             "ordinal_space":ordinal_space,"has_b_frames":has_b_frames,"pts_equals_dts":pts_equals_dts,
             "dts_evidence_required":reorder_required,"composition_offsets":composition_offsets,
             "dts_ticks":dts_ticks,
             # FR-01 authority reference: the byte source this declaration was measured from. A
             # consumer must be able to re-measure it (see `is_binding_eligible`); a record whose
             # entry names no byte source is structural only and can never bind.
             BYTE_AUTHORITY_FIELD:{"container_path":str(container_path) if container_path else None,
                                   "measurement_artifact_path":(str(measurement_artifact_path)
                                                                if measurement_artifact_path else None),
                                   "selected_stream_index":selected_stream_index}}
    if snapshot_evidence is not None:
        binding[BYTE_AUTHORITY_FIELD]["snapshot_evidence"]=dict(snapshot_evidence)
    if request_identity is not None:
        # The C2 entry is covered by Gate-3's refinement evidence digest, so the
        # request/attempt identity is cryptographically bound with the measured bytes.
        binding["request_identity"]=dict(request_identity)
    binding_origin={"kind":authority.ORIGIN_NAMED_BYTES if mode=="named_bytes_remeasured"
                    else authority.ORIGIN_MEASUREMENT_ARTIFACT,
                    "ref":str(container_path) if mode=="named_bytes_remeasured"
                    else str(measurement_artifact_path)}
    binding["origin"]=binding_origin
    validation=[{"check":"T7_vfr_classification","vfr":vfr,"measured_reference_period":f"{p.numerator}/{p.denominator}" if p else None,"governing_basis":vfr_basis,"declared_rate_deviation":deviation},
                binding]
    if ordinal_space:
        validation.append({"check":T8_CHECK,"has_b_frames":has_b_frames,"pts_equals_dts":pts_equals_dts,
                           "dts_evidence_required":reorder_required,"dts_ticks":dts_ticks,
                           "composition_offsets":composition_offsets,
                           "result":"DTS_EVIDENCE_RECORDED" if reorder_required else "DTS_EVIDENCE_NOT_REQUIRED"})
    record={"refinement_id":f"ref_{digest[:16]}","attempt_id":attempt_id,"source_revision_id":source_revision_id,
            "source_content_digest":facts["source_bytes_sha256"],"stream_index":facts["stream_index"],
            "evidence_class":"MEASURED","time_domain":time_domain,"precision":precision,
            "start_ticks":start,"end_ticks":end,"endpoint_semantics":"half_open",
            "end_is_stream_tail":end_tail,"time_base":{"num":table.time_base.num,"den":table.time_base.den},
            "method":{"tool":tool_identity,
                      "derivation":TAIL_DERIVATION if end_tail else (ORDINAL_DERIVATION if ordinal_space else PTS_DERIVATION),
                      "retained_enumeration":bool(retain_enumeration)},
            "validation_results":validation,"method_kind":"deterministic","replay_availability":"replayable",
            "frame_ordinal_basis":basis.basis() if ordinal_space else None,
            "uncertainty":[],"produced_by_gate3_refinement_attempt":True}
    if end_tail:
        record["extent_state"]=tail_detail["extent_state"]
        record["last_frame_extent"]=None
        record["tail_measurement_ref"]=f"{TAIL_REFERENCE_CHECK}:{facts['source_bytes_sha256']}"
        record["uncertainty"]=[
            {"check":TAIL_REFERENCE_CHECK,"scope":"tail","boundary":"interval_end","state":"DERIVED_NOT_OBSERVED",
             "extent_state":tail_detail["extent_state"],"derivation":tail_detail["derivation"],
             "measured_source_digest":tail_detail["measured_source_digest"],
             "tail_end_ticks":tail_detail["tail_end_ticks"],"container_facts":tail_detail["container_facts"]},
            {"check":TAIL_REFERENCE_CHECK,"scope":"tail","boundary":"last_frame_extent","state":"UNCERTAIN",
             "derivation":"unobservable at a stream tail: no next presentation PTS"},
        ]
    record["evidence_digest"]=authority.evidence_digest(RECORD_KIND_REFINEMENT,record)
    return record
