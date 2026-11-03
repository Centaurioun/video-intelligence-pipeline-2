"""Minimal ISO-BMFF timing measurement against named synthetic container bytes.

FR-02: presentation PTS is computed from ``stts`` (decode DTS) plus ``ctts``
composition offsets, the selected stream is an explicit *video* ``trak``, and
unsupported ``ctts``/``elst``/ambiguous-multi-track shapes fail closed with a
deterministic, attributable reason instead of being silently reinterpreted.
"""
from __future__ import annotations
import hashlib,pathlib,struct
from collections.abc import Mapping
DERIVATION="iso-bmff: mdhd.timescale + stts + elst"
CTTS_DERIVATION_SUFFIX=" + ctts composition offsets"
VIDEO_HANDLER=b"vide"
SOLE_VIDEO_DERIVATION="sole_timing_bearing_video_trak"
EXPLICIT_SELECTION_DERIVATION="explicitly_selected_trak_ordinal"
MEASUREMENT_ARTIFACT_FIELDS=("source_bytes_sha256","media_timescale","nb_frames","duration_ts",
                             "duration_consistency","pts_ticks","stream_index","stream_count")
# FR-01: a persisted measurement artifact may only create binding authority when it *names* the
# bytes it measured.  These are the declared byte-source fields the canonical in-repo producers
# and the persisted-artifact fixtures use: an explicit source path and/or a list of the files the
# producer claims hash to the declared digest.  Naming a file is never sufficient by itself -- the
# bytes are read and hashed here (see `_resolved_byte_source_path`), so a self-asserted digest
# string or a false file listing cannot manufacture authority.
BYTE_SOURCE_PATH_FIELDS=("source_path","container_path")
BYTE_SOURCE_LIST_FIELDS=("files_hashing_to_declared_digest",)


def _exact_int(value):
    """In-repo type-aware integer identity: ``bool`` is not an integer here (FR-10/MAJOR-B)."""
    return isinstance(value,int) and not isinstance(value,bool)


def _resolved_byte_source_path(artifact,digest):
    """Return a declared byte-source path whose real bytes hash to ``digest``, else ``None``.

    Only paths the artifact itself declares are considered, and each candidate is opened and
    re-hashed: the declared digest string is never trusted on its own, and a
    ``files_hashing_to_declared_digest`` entry that does not actually hash to the declared
    digest is ignored.  Returns ``None`` when no declared byte source resolves.
    """
    candidates=[]
    for field in BYTE_SOURCE_PATH_FIELDS:
        value=artifact.get(field)
        if isinstance(value,str) and value:candidates.append(value)
    for field in BYTE_SOURCE_LIST_FIELDS:
        value=artifact.get(field)
        if isinstance(value,(list,tuple)):
            candidates.extend(item for item in value if isinstance(item,str) and item)
    seen=set()
    for candidate in candidates:
        if candidate in seen:continue
        seen.add(candidate)
        try:
            path=pathlib.Path(candidate)
            if not path.is_file():continue
            if hashlib.sha256(path.read_bytes()).hexdigest()==digest:return str(path)
        except OSError:
            continue
    return None
def _boxes(raw,start=0,end=None):
    end=len(raw) if end is None else end;pos=start
    while pos+8<=end:
        size,typ=struct.unpack_from(">I4s",raw,pos)
        header=8
        if size == 1:
            if pos + 16 > end:
                raise ValueError("invalid large-size box")
            size=struct.unpack_from(">Q",raw,pos+8)[0]
            header=16
        elif size == 0:
            size=end-pos
        if size<header or pos+size>end:raise ValueError("invalid box")
        yield typ,pos+header,pos+size,pos
        pos+=size
def _find(raw,typ,start=0,end=None):
    for t,a,b,p in _boxes(raw,start,end):
        if t==typ:return a,b,p
    return None
def _find_path(raw,path,start=0,end=None):
    cur=(start,len(raw) if end is None else end,None)
    for typ in path:
        f=_find(raw,typ,cur[0],cur[1])
        if not f:return None
        cur=f
    return cur
def _parse_full_header(raw,a):return a+4
def _parse_mdhd(raw,a):
    p=_parse_full_header(raw,a); _c,_m,ts,d=struct.unpack_from(">IIII",raw,p);return ts,d
def _parse_hdlr(raw,a):
    p=_parse_full_header(raw,a);return bytes(raw[p+4:p+8])
def _parse_stts(raw,a):
    p=_parse_full_header(raw,a);n=struct.unpack_from(">I",raw,p)[0];p+=4;out=[]
    for _ in range(n):
        c,d=struct.unpack_from(">II",raw,p);p+=8;out.extend([d]*c)
    return tuple(out)
def _parse_ctts(raw,box,sample_count):
    """Return per-sample composition offsets; refuse unsupported ``ctts`` forms.

    Accepts both the Gate-3 synthetic layout (``entry_count`` then one offset per sample)
    and the ISO layout (``entry_count`` then ``(run_count, offset)`` pairs expanding to
    exactly ``sample_count`` samples).  Anything else is an unsupported ``ctts`` and fails
    closed rather than being reinterpreted as presentation order.
    """
    a,b,_p=box;payload=_parse_full_header(raw,a);version=raw[payload-4]
    if version not in (0,1):
        raise ValueError(f"unsupported ctts version {version}: composition offsets cannot be interpreted")
    n=struct.unpack_from(">I",raw,payload)[0];p=payload+4
    entry_bytes=(b-p)-0
    expanded=[]
    if entry_bytes==4*sample_count:
        fmt=">i" if version==1 else ">I"
        expanded=[struct.unpack_from(fmt,raw,p+4*i)[0] for i in range(sample_count)]
    elif n>0 and entry_bytes>=8*n:
        for _ in range(n):
            count,offset=struct.unpack_from(">Ii" if version==1 else ">II",raw,p);p+=8
            if count<=0:raise ValueError("unsupported ctts: zero-length composition run")
            expanded.extend([offset]*count)
    else:
        raise ValueError("unsupported ctts: composition offset table does not cover the decoded samples")
    if len(expanded)!=sample_count:
        raise ValueError(f"unsupported ctts entry count {len(expanded)}: composition offsets do not cover the {sample_count} decoded samples")
    if version==0 and any(o<0 for o in expanded):raise ValueError("unsupported ctts version 0 negative composition offset")
    return tuple(expanded)
def _parse_elst(raw,a):
    """Return a single non-negative edit-list media time; refuse every other form."""
    p=_parse_full_header(raw,a);n=struct.unpack_from(">I",raw,p)[0];p+=4
    if n<1:raise ValueError("unsupported edit list (elst): entry_count<1 has no deterministic origin mapping")
    if n>1:raise ValueError("unsupported edit list (elst): multiple segments have no deterministic origin mapping")
    _seg,media_time=struct.unpack_from(">Ii",raw,p)
    if media_time<0:raise ValueError("unsupported edit list (elst): negative media_time has no deterministic origin mapping")
    return media_time
def _trak_timing(raw,a,b):
    md=_find_path(raw,[b"mdia",b"mdhd"],a,b);st=_find_path(raw,[b"mdia",b"minf",b"stbl",b"stts"],a,b)
    hl=_find_path(raw,[b"mdia",b"hdlr"],a,b)
    if not (md and st):return None
    deltas=_parse_stts(raw,st[0])
    if not deltas:return None
    handler=_parse_hdlr(raw,hl[0]) if hl else None
    return {"a":a,"b":b,"mdhd":md,"stts":st,"deltas":deltas,"handler":handler}
def _select_stream(timing,selected_stream_index):
    video=[t for t in timing if t["handler"]==VIDEO_HANDLER]
    if selected_stream_index is not None:
        if not isinstance(selected_stream_index,int) or isinstance(selected_stream_index,bool) or selected_stream_index<0:
            raise ValueError("selected stream index must be a non-negative integer")
        matches=[t for t in timing if t["traks_index"]==selected_stream_index]
        if not matches:
            raise ValueError(f"selected stream {selected_stream_index} has no timing-bearing trak in these bytes")
        if matches[0]["handler"]!=VIDEO_HANDLER:
            raise ValueError(f"selected stream {selected_stream_index} is not a video (vide) timing trak")
        return matches[0],EXPLICIT_SELECTION_DERIVATION
    if len(video)==1:return video[0],SOLE_VIDEO_DERIVATION
    if not video:
        raise ValueError("no timing-bearing video trak: the selected stream must be an explicit video stream")
    raise ValueError(f"ambiguous container: {len(video)} timing-bearing video traks require an explicit selected stream selector")
def parse_iso_bmff_timing_bytes(raw,*,selected_stream_index=None):
    """Parse timing from already-materialized container bytes.

    ``raw`` may be any bytes-like buffer (``bytes``/``bytearray``/read-only
    ``memoryview``); the bytes are never mutated.  This entry point exists so a
    caller that already holds digest-verified snapshot bytes can share them with
    the box-bounds validator instead of reading the whole file a second time.
    """
    moov=_find(raw,b"moov")
    if not moov:raise ValueError("moov missing")
    traks=[x for x in _boxes(raw,moov[0],moov[1]) if x[0]==b"trak"]
    timing=[]
    for idx,(_t,a,b,_p) in enumerate(traks):
        t=_trak_timing(raw,a,b)
        if t:t["traks_index"]=idx;timing.append(t)
    if not timing:raise ValueError("no timing-bearing trak")
    selected,identity=_select_stream(timing,selected_stream_index)
    stream_index=selected["traks_index"];a,b=selected["a"],selected["b"]
    ts,dur=_parse_mdhd(raw,selected["mdhd"][0]);deltas=selected["deltas"]
    dts=[];cur=0
    for delta in deltas:
        dts.append(cur);cur+=delta
    ct=_find_path(raw,[b"mdia",b"minf",b"stbl",b"ctts"],a,b)
    if ct is not None:
        offsets=_parse_ctts(raw,ct,len(deltas))
        pts=[d+o for d,o in zip(dts,offsets)]
        if any(p<0 for p in pts):raise ValueError("unsupported ctts: composition offsets produce a negative presentation PTS")
        derivation=DERIVATION+CTTS_DERIVATION_SUFFIX
    else:
        offsets=tuple([0]*len(deltas));pts=list(dts);derivation=DERIVATION
    presentation=sorted(pts)
    reordered=tuple(pts)!=tuple(dts)
    tail=deltas[-1];computed=presentation[-1]+tail
    el=_find_path(raw,[b"edts",b"elst"],a,b)
    origin=_parse_elst(raw,el[0]) if el else 0
    return {"media_timescale":ts,"duration_ts":dur,"duration_consistency":"MATCH" if dur==computed else "MISMATCH",
            # ``pts_ticks`` is the retained presentation-order enumeration used
            # by PtsTable and refinement.  Keep decode-order evidence separate
            # in ``dts_ticks``; callers must not feed decode order to a
            # presentation-time table when composition offsets reorder frames.
            "pts_ticks":tuple(presentation),"presentation_pts_ticks":tuple(presentation),"dts_ticks":tuple(dts),
            "composition_offsets":tuple(offsets),"has_b_frames":1 if reordered else 0,
            "pts_equals_dts":not reordered,"tail_duration_ticks":tail,"nb_frames":len(pts),
            "media_time_offset":origin,"presentation_origin_ticks":origin,"stream_index":stream_index,
            "stream_count":len(traks),"stream_handler":(selected["handler"] or b"").decode("ascii","replace"),
            "stream_identity_derivation":identity,"selected_stream_index":stream_index,
            "derivation":derivation,"source_bytes_sha256":hashlib.sha256(raw).hexdigest()}
def parse_iso_bmff_timing(path,*,selected_stream_index=None):
    """Measure timing from the whole file at ``path`` (convenience entry point)."""
    return parse_iso_bmff_timing_bytes(pathlib.Path(path).read_bytes(),selected_stream_index=selected_stream_index)
def verified_measurement_artifact(artifact,*,require_resolved_bytes=False):
    """Validate a persisted measurement artifact as an admissible byte-bound basis.

    A caller-provided table alone may never create binding authority (FR-01).  A persisted
    measurement artifact is admissible only when it is the canonical, internally consistent
    record shape this module emits: it must name the source bytes by digest, enumerate integer
    presentation PTS retained in order, declare a positive media timescale and a non-negative
    ``stream_index``, and recompute its own duration consistency.  Returns ``(facts, None)`` on
    success and ``(None, reason)`` otherwise.

    ``require_resolved_bytes`` is the FR-01 authority switch.  When true the artifact must also
    *name the bytes it measured* -- via ``source_path``/``container_path`` or
    ``files_hashing_to_declared_digest`` -- and that byte source is opened, re-hashed against the
    declared digest and re-measured, so every declared fact is recompute-verified against the
    named bytes.  An artifact whose declared digest resolves to no bytes, or whose declared facts
    the named bytes contradict, fails closed.  Every binding-authority consumer in
    ``gate3.refinement`` requests resolution; the shape-only default exists for schema and
    producer/schema-agreement consumers that hold no byte authority
    (``tests/gate3/test_gen2_r8_stream_index_type_authority.py`` pins that surface).
    """
    if not isinstance(artifact,Mapping):return None,"MEASUREMENT_ARTIFACT_NOT_AN_OBJECT"
    for field in MEASUREMENT_ARTIFACT_FIELDS:
        if field not in artifact:return None,f"MEASUREMENT_ARTIFACT_MISSING_{field.upper()}"
    digest=artifact.get("source_bytes_sha256")
    if not isinstance(digest,str) or not digest:return None,"MEASUREMENT_ARTIFACT_DIGEST_NOT_A_NON_EMPTY_STRING"
    ts=artifact.get("media_timescale")
    if not _exact_int(ts) or ts<=0:return None,"MEASUREMENT_ARTIFACT_TIMESCALE_NOT_POSITIVE_INTEGER"
    pts=artifact.get("pts_ticks")
    if isinstance(pts,(str,bytes)) or not isinstance(pts,(list,tuple)) or not pts:return None,"MEASUREMENT_ARTIFACT_PTS_NOT_A_NON_EMPTY_SEQUENCE"
    if any(not _exact_int(t) for t in pts):return None,"MEASUREMENT_ARTIFACT_PTS_NOT_INTEGERS"
    if any(b<a for a,b in zip(pts,pts[1:])):return None,"MEASUREMENT_ARTIFACT_PTS_NOT_MONOTONIC"
    # MAJOR-B: `nb_frames` is an exact integer frame count, exactly like the timescale/stream/
    # duration fields below.  A bare `!=` would admit `1.0` for any count and `True` for a
    # 1-frame artifact.
    if not _exact_int(artifact.get("nb_frames")):return None,"MEASUREMENT_ARTIFACT_NB_FRAMES_NOT_AN_EXACT_INTEGER"
    if artifact.get("nb_frames")!=len(pts):return None,"MEASUREMENT_ARTIFACT_NB_FRAMES_INCONSISTENT_WITH_PTS"
    si=artifact.get("stream_index")
    if not _exact_int(si) or si<0:return None,"MEASUREMENT_ARTIFACT_STREAM_INDEX_NOT_A_NON_NEGATIVE_INTEGER"
    sc=artifact.get("stream_count")
    if not _exact_int(sc) or sc<0:return None,"MEASUREMENT_ARTIFACT_STREAM_COUNT_NOT_A_NON_NEGATIVE_INTEGER"
    dur=artifact.get("duration_ts");consistency=artifact.get("duration_consistency")
    if not _exact_int(dur) or dur<=0:return None,"MEASUREMENT_ARTIFACT_DURATION_TS_NOT_POSITIVE_INTEGER"
    if consistency not in ("MATCH","MISMATCH"):return None,"MEASUREMENT_ARTIFACT_DURATION_CONSISTENCY_NOT_DECLARED"
    tail=artifact.get("tail_duration_ticks")
    if tail is None:
        # The canonical persisted `measurement_record` shape carries no tail delta; the
        # duration must still extend beyond the last enumerated presentation PTS.
        if not (dur>pts[-1] and consistency=="MATCH"):
            return None,"MEASUREMENT_ARTIFACT_DURATION_CONSISTENCY_DOES_NOT_RECOMPUTE"
    else:
        if not _exact_int(tail) or tail<=0:
            return None,"MEASUREMENT_ARTIFACT_TAIL_DURATION_NOT_POSITIVE_INTEGER"
        if (dur==pts[-1]+tail) != (consistency=="MATCH"):
            return None,"MEASUREMENT_ARTIFACT_DURATION_CONSISTENCY_DOES_NOT_RECOMPUTE"
    facts={"source_bytes_sha256":digest,"media_timescale":ts,"pts_ticks":tuple(pts),"nb_frames":len(pts),
           "stream_index":si,"stream_count":sc,"duration_ts":dur,"duration_consistency":consistency,
           "tail_duration_ticks":tail}
    if not require_resolved_bytes:return facts,None
    # FR-01 authority step: resolve the declared digest to real bytes and recompute-verify every
    # declared fact against them.  A self-asserted digest string is never sufficient.
    resolved=_resolved_byte_source_path(artifact,digest)
    if resolved is None:return None,"MEASUREMENT_ARTIFACT_DECLARED_BYTES_NOT_RESOLVED"
    try:
        measured=parse_iso_bmff_timing(resolved,selected_stream_index=si)
    except (OSError,ValueError) as exc:
        return None,f"MEASUREMENT_ARTIFACT_NAMED_BYTES_UNMEASURABLE:{exc}"
    if measured["source_bytes_sha256"]!=digest:return None,"MEASUREMENT_ARTIFACT_DECLARED_BYTES_NOT_RESOLVED"
    if (tuple(measured["pts_ticks"])!=tuple(pts) or measured["media_timescale"]!=ts
            or measured["nb_frames"]!=len(pts) or measured["duration_ts"]!=dur
            or measured["duration_consistency"]!=consistency or measured["stream_count"]!=sc):
        return None,"MEASUREMENT_ARTIFACT_FACTS_DO_NOT_MATCH_NAMED_BYTES"
    # Carry the re-measured reorder facts so the T8 predicate re-derives the DTS requirement from
    # the named bytes rather than from the artifact's or the record's own declaration.
    facts.update({"has_b_frames":measured.get("has_b_frames"),
                  "pts_equals_dts":measured.get("pts_equals_dts"),
                  "dts_ticks":measured.get("dts_ticks"),
                  "composition_offsets":measured.get("composition_offsets"),
                  "presentation_origin_ticks":measured.get("presentation_origin_ticks")})
    return facts,None
