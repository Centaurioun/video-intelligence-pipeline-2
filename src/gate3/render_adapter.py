"""Narrow deterministic synthetic test-harness render adapter; NOT a production renderer.

FR-15 / R-02.g.1: the rendered artifact is attributed by the bytes it ACTUALLY WROTE, and admission to
the adapter is a CHECKED condition (synthetic fixture bytes, well-formed synthetic placement, complete
provenance, non-production scope) rather than a self-declared flag.
"""
from __future__ import annotations
import hashlib,json,pathlib
# FR-13/R-13 §9.1 domain identity: an interval is only comparable/attributable inside an identified
# timeline domain, so resolving an A.6 id requires an identifiable one.
from gate3.placement import timeline_domain_identity

ADAPTER_ID="gate3.synthetic-render.v0"
RENDER_KIND="SYNTHETIC_TEST_HARNESS"
SYNTHETIC_SCOPE="SYNTHETIC_FIXTURE"
PRODUCTION_SCOPES=("REAL","PRODUCTION")
ARTIFACT_ATTEMPT="synthetic-render-attempt"
PLACEMENT_KEYS=("placement_id","timeline_start_ticks","timeline_end_ticks","source_interval")
# FR-10/A.6 (normative Appendix A.6 body, implementation plan line 7957) types a plan's
# ``placements`` as an array of placement-id STRINGS -- ``{"type":"array","items":{"type":"string"}}``
# -- while A.7 ``timeline_placement`` owns the timeline interval. The plan record therefore carries
# ids only, and the L4 records are supplied alongside so this consumer can RESOLVE each id.
#
# These are the ONLY accepted names for that record source. ``placements`` is deliberately NOT one: it
# is the plan's own A.6 id list, so accepting it would alias the id list as the record set and let an
# id "resolve" to itself.
PLACEMENT_RECORD_KWARGS=("placement_records","resolved_placements","timeline_placements")
# A.7 identity/interval fields. An id may only be RESOLVED from a record carrying all of them: a
# minimal ``{placement_id, timeline_start_ticks, timeline_end_ticks}`` object is not a timeline
# placement, and resolving an id from one would manufacture a rendered interval for an id the plan
# pinned elsewhere (false render authority through the A.6 seam). Enforced on RESOLUTION only; the
# inline checked dict-segment form is unchanged.
A7_STRING_REFS=("source_interval_ref","editorial_decision_ref","mapping_artifact_ref")
A7_REQUIRED_FIELDS=("placement_id","plan_id","plan_revision","source_interval_ref",
                    "editorial_decision_ref","track","order_index","timeline_start_ticks",
                    "timeline_end_ticks","mapping_artifact_ref","timeline_domain")


def _is_int(v):return isinstance(v,int) and not isinstance(v,bool)


def _require(cond,msg):
    if not cond:raise ValueError(msg)


def _checked_placement(placement):
    """Checked admission for a placement: a mapping with a well-formed, non-production interval.

    Accepts both the Task-35 plan-segment shape (`timeline_start_ticks`/`timeline_end_ticks`) and the
    minimal legacy shape (`start`/`end`); a non-mapping or a degenerate/inverted/production-scoped
    placement is refused.
    """
    _require(isinstance(placement,dict),"unrecognized placement shape")
    _require(placement.get("scope") not in PRODUCTION_SCOPES,"production-scoped placement is refused")
    start=placement.get("timeline_start_ticks",placement.get("start"))
    end=placement.get("timeline_end_ticks",placement.get("end"))
    _require(_is_int(start) and _is_int(end),"placement interval must be integers")
    _require(end>start,"inverted or degenerate placement interval is refused")
    return start,end


def _placement_record_id(record):
    """The ``placement_id`` of an L4 placement, from an A.7 mapping or the record model.

    Returns ``None`` (never raises) when the value is not an identifiable placement record, so the
    caller can fail closed with the shape error rather than leaking a lookup failure.
    """
    if isinstance(record,str):
        return record or None
    if isinstance(record,dict):
        pid=record.get("placement_id")
    else:
        pid=getattr(record,"placement_id",None)
    return pid if isinstance(pid,str) and pid else None


def _placement_records_index(records):
    """Index L4 placement records by their placement id, refusing an ambiguous duplicate id."""
    index={}
    for record in records or ():
        pid=_placement_record_id(record)
        if pid is None:continue
        if pid in index and index[pid] is not record:
            raise ValueError("ambiguous duplicate placement_id is refused")
        index[pid]=record
    return index


def _a7_field(record,name):
    """One A.7 field, from an A.7 mapping (key form) or the ``TimelinePlacement`` record (attribute)."""
    if isinstance(record,dict):return record.get(name)
    return getattr(record,name,None)


def _a7_placement_record(record):
    """The A.7 identity of a record resolvable by placement id, or ``None`` when it is not one.

    ADMISSION, not a convenience projection: an id may only be resolved from a record that actually
    IS an A.7 ``timeline_placement`` -- ``placement_id``/``plan_id``/``source_interval_ref``/
    ``editorial_decision_ref``/``track``/``mapping_artifact_ref`` present as non-empty strings,
    ``plan_revision``/``order_index`` exact integers (never bool), an identifiable
    ``timeline_domain``, and exact-integer ticks with ``end > start``. A ``TimelinePlacement``
    instance is accepted on the same terms via its attributes. Anything else returns ``None`` and the
    caller fails closed: a partial object must never be able to manufacture a rendered interval.
    """
    pid=_a7_field(record,"placement_id")
    if not isinstance(pid,str) or not pid:return None
    for name in ("plan_id","track")+A7_STRING_REFS:
        value=_a7_field(record,name)
        if not isinstance(value,str) or not value:return None
    plan_revision=_a7_field(record,"plan_revision")
    order_index=_a7_field(record,"order_index")
    if not _is_int(plan_revision) or not _is_int(order_index):return None
    start=_a7_field(record,"timeline_start_ticks");end=_a7_field(record,"timeline_end_ticks")
    if not _is_int(start) or not _is_int(end):return None
    if end<=start:return None
    domain=_a7_field(record,"timeline_domain")
    # FR-13/R-13 §9.1: a timeline domain is identified by its name plus exact time base; an
    # unidentifiable domain makes the interval non-comparable and must not be resolved.
    try:timeline_domain_identity(domain)
    except ValueError:return None
    return {"placement_id":pid,"plan_id":_a7_field(record,"plan_id"),"plan_revision":plan_revision,
            "source_interval_ref":_a7_field(record,"source_interval_ref"),
            "editorial_decision_ref":_a7_field(record,"editorial_decision_ref"),
            "track":_a7_field(record,"track"),"order_index":order_index,
            "mapping_artifact_ref":_a7_field(record,"mapping_artifact_ref"),
            "timeline_start_ticks":start,"timeline_end_ticks":end}


def _timeline_segment(record):
    """Project a WELL-FORMED A.7 placement record onto the renderer's checked segment shape.

    Returns ``None`` when the record is not an admissible A.7 placement, so the caller fails closed
    with the canonical shape error rather than rendering an interval the plan never pinned.
    """
    identity=_a7_placement_record(record)
    if identity is None:return None
    segment={"placement_id":identity["placement_id"],
             "timeline_start_ticks":identity["timeline_start_ticks"],
             "timeline_end_ticks":identity["timeline_end_ticks"],
             "source_interval_ref":identity["source_interval_ref"],
             "track":identity["track"],
             "mapping_artifact_ref":identity["mapping_artifact_ref"]}
    source_interval=_a7_field(record,"source_interval")
    if isinstance(source_interval,(tuple,list)) and len(source_interval)==2:
        segment["source_interval"]=tuple(source_interval)
    return segment


def _plan_cross_bind(plan,identity):
    """Refuse a record whose plan identity contradicts the plan record being rendered.

    FR-15 requires an attributable reverse mapping, so the resolved record must be the one THIS plan
    pinned. ``plan_id``/``plan_revision`` are compared only when the plan record declares them: the
    production record always does (``EditPlanRevision.to_record()``), but a partial plan record must
    not be over-rejected on a key it legitimately omits (noted in the lane memo).
    """
    plan_id=plan.get("plan_id")
    if plan_id is not None:
        _require(isinstance(plan_id,str) and plan_id,
                 "plan record's plan_id must be a non-empty string")
        _require(identity["plan_id"]==plan_id,
                 "resolved placement belongs to a different plan")
    plan_revision=plan.get("plan_revision")
    if plan_revision is not None:
        _require(_is_int(plan_revision),
                 "plan record's plan_revision must be an integer")
        _require(identity["plan_revision"]==plan_revision,
                 "resolved placement belongs to a different plan revision")


def render_synthetic(*,source_path,out_path,placement,mapping_artifact_ref,producer_attempt_id):
    """Render a synthetic artifact and attribute it by its own measured output bytes."""
    _require(isinstance(mapping_artifact_ref,str) and mapping_artifact_ref.strip(),
             "mapping_artifact_ref must be a non-empty provenance ref")
    _require(isinstance(producer_attempt_id,str) and producer_attempt_id.strip(),
             "producer_attempt_id must be a non-empty provenance ref")
    _checked_placement(placement)
    src=pathlib.Path(source_path).read_bytes()
    # Checked synthetic admission: only named synthetic fixture bytes (ISO-BMFF) are admitted.
    _require(len(src)>=8 and src[4:8]==b"ftyp","non-fixture source bytes are not admitted")
    source_digest=hashlib.sha256(src).hexdigest()
    envelope={"adapter_id":ADAPTER_ID,"render_kind":RENDER_KIND,"scope":SYNTHETIC_SCOPE,
              "placement":dict(placement),"mapping_artifact_ref":mapping_artifact_ref,
              "producer_attempt_id":producer_attempt_id,"source_digest":source_digest}
    blob=(b"G3RENDER\0"+hashlib.sha256(src).digest()+
          json.dumps(envelope,sort_keys=True,default=str).encode())
    p=pathlib.Path(out_path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
    written=p.read_bytes()                      # measure what was actually written
    digest=hashlib.sha256(written).hexdigest()
    return {"artifact_id":"render_"+digest[:16],"artifact_type":"rendered_output","digest":digest,
            "digest_algorithm":"sha256","byte_count":len(written),"parents":[source_digest],
            "producer_attempt_id":producer_attempt_id,"mapping_artifact_ref":mapping_artifact_ref,
            "scope":SYNTHETIC_SCOPE,"render_kind":RENDER_KIND,"adapter_id":ADAPTER_ID,
            "time_domain":"rendered_output","production_eligible":False,
            "production_renderer_selected":False,"path":str(p)}


def verify_rendered_output(artifact):
    """Re-measure a rendered artifact against its bytes on disk. Tampering fails closed (ValueError)."""
    _require(isinstance(artifact,dict),"rendered artifact must be a mapping")
    path=artifact.get("path")
    _require(isinstance(path,str) and path.strip(),"rendered artifact must name its output path")
    p=pathlib.Path(path)
    _require(p.is_file(),"rendered artifact bytes are absent")
    written=p.read_bytes()
    _require(artifact.get("digest")==hashlib.sha256(written).hexdigest(),
             "rendered output bytes do not match the recorded digest")
    _require(artifact.get("byte_count")==len(written),
             "rendered output byte count does not match the recorded attribution")
    _require(artifact.get("digest_algorithm")=="sha256","unexpected rendered digest algorithm")
    _require(artifact.get("production_eligible") is False,
             "a production-eligible artifact cannot be a synthetic render")
    _require(artifact.get("scope")==SYNTHETIC_SCOPE,
             "rendered artifact scope must be the checked synthetic scope")
    return True


validate_rendered_output=verify_rendered_output
revalidate_rendered_output=verify_rendered_output
re_measure_rendered_output=verify_rendered_output
verify_output=verify_rendered_output
validate_output=verify_rendered_output


class SyntheticRenderAdapter:
    """Task 35 synthetic test-harness adapter. Synthetic only; never production."""
    adapter_id=ADAPTER_ID
    render_kind=RENDER_KIND
    # A checked property, not a caller-declared literal: this adapter never selects a production renderer.
    production_renderer_selected=False

    def render(self,plan,**kwargs):
        """Render a plan. Production scope is REFUSED; a synthetic plan renders deterministically.

        FR-10/A.6: the plan record carries placement-id STRINGS (A.6) while A.7 owns the timeline
        interval, so an id is RESOLVED to its L4 record via the ``PLACEMENT_RECORD_KWARGS`` records.
        The checked dict-segment form keeps working unchanged: a mapping carrying its own
        ``timeline_start_ticks``/``timeline_end_ticks`` needs no external resolution. Resolution never
        weakens admission -- every resolved segment passes ``_checked_placement``, and an id that
        resolves to nothing is still refused as an unrecognized placement shape.
        """
        _require(isinstance(plan,dict),"unrecognized plan shape")
        _require(plan.get("plan_scope") not in PRODUCTION_SCOPES,
                 "production-scoped plan is refused by the synthetic adapter")
        placements=self._plan_placements(plan,kwargs)
        out_path=kwargs.get("out_path")
        if out_path is None:
            import tempfile
            out_path=str(pathlib.Path(tempfile.mkdtemp(prefix="fr15-render-"))/"rendered.bin")
        payload={"adapter_id":ADAPTER_ID,"render_kind":RENDER_KIND,"scope":SYNTHETIC_SCOPE,"plan":plan}
        blob=b"G3RENDER\0"+json.dumps(payload,sort_keys=True,default=str).encode()
        p=pathlib.Path(out_path);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
        written=p.read_bytes();digest=hashlib.sha256(written).hexdigest()
        artifact={"artifact_id":"render_"+digest[:16],"artifact_type":"rendered_output","digest":digest,
                  "digest_algorithm":"sha256","byte_count":len(written),"scope":SYNTHETIC_SCOPE,
                  "render_kind":RENDER_KIND,"adapter_id":ADAPTER_ID,"production_eligible":False,
                  "production_renderer_selected":False,"plan":plan,"segments":list(placements),
                  "time_domain":"rendered_output","path":str(p)}
        # The rendered timeline hop is expressed as an exact-rational identity over the enumerated
        # rendered ticks, so T10 status is computed (never declared) by FR-04's rule.
        from gate3.mapping import HOP_TIMELINE_TO_RENDERED,MappingArtifact
        ticks=tuple(sorted({int(seg["timeline_start_ticks"]) for seg in placements}|
                           {int(seg["timeline_end_ticks"]) for seg in placements}))
        mapping=MappingArtifact(mapping_id="map_"+digest[:12],artifact_type="mapping_artifact",
                                digest=digest,
                                parents=(digest,)+tuple(str(seg["placement_id"]) for seg in placements),
                                retention="RETAIN",availability="AVAILABLE",
                                hop=HOP_TIMELINE_TO_RENDERED,method="identity",params={},
                                validated_sample=ticks,residual=0,producer_attempt_id=ARTIFACT_ATTEMPT)
        return {"mapping":mapping,"artifact":artifact,"segments":list(placements),
                "adapter_id":ADAPTER_ID,"render_kind":RENDER_KIND,"scope":SYNTHETIC_SCOPE,
                "artifact_id":artifact["artifact_id"],"digest":digest,"path":str(p)}

    @staticmethod
    def _declared_segments(mapping):
        params=getattr(mapping,"params",None)
        if params is None and isinstance(mapping,dict):params=mapping.get("params")
        if not isinstance(params,dict):return []
        raw=params.get("segments") or params.get("samples")
        return list(raw) if isinstance(raw,(list,tuple)) else []

    @staticmethod
    def _resolve_placement_ref(ref,plan,index):
        """Resolve one A.6 placement-id STRING to its checked segment.

        An id the caller supplied no record for cannot own a timeline interval, and a record that is
        not a well-formed A.7 placement (or whose plan identity contradicts this plan) must not be
        allowed to manufacture one. All of these are refused with the canonical shape error -- exactly
        as a non-mapping placement was refused before.
        """
        record=index.get(ref)
        if record is None:raise ValueError("unrecognized placement shape")
        segment=_timeline_segment(record)
        if segment is None:raise ValueError("unrecognized placement shape")
        _plan_cross_bind(plan,_a7_placement_record(record))
        return segment

    @classmethod
    def _plan_placements(cls,plan,kwargs):
        """The checked timeline segments the plan renders, resolving A.6 placement-id strings.

        A mapping segment that carries its own timeline ticks is checked in place; a string element is
        resolved against the L4 placement records supplied under a ``PLACEMENT_RECORD_KWARGS`` name.
        """
        placements=plan.get("placements")
        _require(isinstance(placements,list) and placements,"plan must carry at least one placement")
        records=None
        for name in PLACEMENT_RECORD_KWARGS:
            candidate=kwargs.get(name)
            if isinstance(candidate,(list,tuple)) and candidate:
                records=candidate;break
        index=_placement_records_index(records)
        segments=[]
        for segment in placements:
            if isinstance(segment,str):
                segment=cls._resolve_placement_ref(segment,plan,index)
            else:
                _checked_placement(segment)
            segments.append(segment)
        return segments

    def resolve_output_frame(self,out,frame):
        """Reverse-resolve a rendered coordinate back to source; a CONTRADICTING mapping is refused."""
        _require(isinstance(out,dict),"rendered output must be a mapping")
        mapping=out.get("mapping")
        _require(mapping is not None,"rendered output carries no mapping to resolve through")
        for segment in out.get("segments") or []:
            lo=int(segment["timeline_start_ticks"]);hi=int(segment["timeline_end_ticks"])
            for declared in self._declared_segments(mapping):
                if not isinstance(declared,dict):continue
                rendered=declared.get("rendered");timeline=declared.get("timeline")
                if not (isinstance(rendered,(list,tuple)) and len(rendered)==2):continue
                if not (isinstance(timeline,(list,tuple)) and len(timeline)==2):
                    raise ValueError("mapping segment is not a well-formed 1:1 hop")
                if int(rendered[0])<=int(frame)<=int(rendered[1]) and [int(timeline[0]),int(timeline[1])]!=[lo,hi]:
                    raise ValueError("mapping contradicts the rendered output segments")
        for segment in out.get("segments") or []:
            lo=int(segment["timeline_start_ticks"]);hi=int(segment["timeline_end_ticks"])
            # FR-13 / placement.py:12: every TimelinePlacement is frozen to endpoint_semantics
            # "half_open", so a placement owns [lo, hi) and the boundary tick hi belongs to the NEXT
            # placement on the track (or to nothing when this is the final placement).  An inclusive
            # upper bound mis-attributed that shared boundary tick to the earlier placement, which is
            # a wrong reverse mapping: with contiguous placements [0,100) and [100,200) the rendered
            # coordinate 100 resolved to placement 1, and coordinate 200 -- outside every half-open
            # placement -- still resolved to placement 2.
            if lo<=int(frame)<hi:
                # ``source_interval`` is present only when the segment declares measured source
                # ticks; an id-resolved A.7 segment instead carries the cross-link to the interval
                # it pins, and falls back to the timeline interval (the identity hop) otherwise.
                source_interval=segment.get("source_interval")
                if not (isinstance(source_interval,(tuple,list)) and len(source_interval)==2):
                    source_interval=(lo,hi)
                return {"coordinate_domain":"rendered_output","timeline_tick":int(frame),
                        "timeline_interval":(lo,hi),
                        "source_interval":tuple(source_interval),
                        "source_interval_ref":segment.get("source_interval_ref"),
                        "placement_id":segment.get("placement_id")}
        return {"coordinate_domain":"rendered_output","timeline_tick":int(frame),
                "timeline_interval":None,"source_interval":None,"placement_id":None}
    def verify_rendered_output(self,artifact):return verify_rendered_output(artifact)
    def validate_rendered_output(self,artifact):return verify_rendered_output(artifact)
    def render_plan(self,plan,*args,**kwargs):
        scope=plan.get("plan_scope") if isinstance(plan,dict) else None
        _require(scope not in PRODUCTION_SCOPES,"production-scoped plan is refused by the synthetic adapter")
        return self.render(*args,**kwargs)
