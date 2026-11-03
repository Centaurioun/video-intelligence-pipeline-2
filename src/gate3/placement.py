from collections.abc import Mapping
from dataclasses import dataclass
from gate3.timeline import TimelineDomain
INITIAL_PLAYBACK_SPEED="1.0";INITIAL_TRANSITION="HARD_CUT"
@dataclass(frozen=True)
class TimelinePlacement:
    placement_id:str;plan_id:str;plan_revision:int;source_interval_ref:str|None;editorial_decision_ref:str|None;track:str;order_index:int|None;timeline_start_ticks:int;timeline_end_ticks:int;mapping_artifact_ref:str|None;timeline_domain:TimelineDomain;playback_speed:str=INITIAL_PLAYBACK_SPEED;transition:str=INITIAL_TRANSITION;endpoint_semantics:str="half_open"
    def __post_init__(self):
        if not self.source_interval_ref or not self.editorial_decision_ref or not self.mapping_artifact_ref:raise ValueError("required refs missing")
        if self.order_index is None:raise ValueError("order_index required")
        if self.timeline_end_ticks<=self.timeline_start_ticks:raise ValueError("invalid interval")
        if self.playback_speed!=INITIAL_PLAYBACK_SPEED or self.transition!=INITIAL_TRANSITION or self.endpoint_semantics!="half_open":raise ValueError("outside initial scope")
    def to_record(self):return {"placement_id":self.placement_id,"plan_id":self.plan_id,"plan_revision":self.plan_revision,"source_interval_ref":self.source_interval_ref,"editorial_decision_ref":self.editorial_decision_ref,"track":self.track,"order_index":self.order_index,"timeline_start_ticks":self.timeline_start_ticks,"timeline_end_ticks":self.timeline_end_ticks,"mapping_artifact_ref":self.mapping_artifact_ref,"timeline_domain":{"domain_id":self.timeline_domain.domain_id,"time_base":{"num":self.timeline_domain.time_base.num,"den":self.timeline_domain.time_base.den}},"playback_speed":self.playback_speed,"transition":self.transition,"endpoint_semantics":self.endpoint_semantics}
def timeline_domain_identity(domain):
    # A timeline domain's declared coordinate space is its attributable name plus its
    # exact time base. FR-13/R-13 §9.1: no authority read licenses converting ticks
    # between two declared domains, so identity -- not raw ticks -- decides comparability.
    if isinstance(domain,TimelineDomain):return (domain.domain_id,domain.time_base.num,domain.time_base.den)
    if isinstance(domain,Mapping):
        tb=domain.get("time_base")
        if isinstance(tb,Mapping):return (domain.get("domain_id"),tb.get("num"),tb.get("den"))
    raise ValueError("unidentifiable timeline domain")
def placement_interval(p):
    # Complete timeline placement -> (track,start,end,domain_identity); None when the
    # entry is not a timeline placement at all (e.g. a bare placement-id string or a
    # partial record owned by another validation path).
    if isinstance(p,Mapping):
        track,start,end,domain=(p.get("track"),p.get("timeline_start_ticks"),p.get("timeline_end_ticks"),p.get("timeline_domain"))
    else:
        track,start,end,domain=(getattr(p,"track",None),getattr(p,"timeline_start_ticks",None),getattr(p,"timeline_end_ticks",None),getattr(p,"timeline_domain",None))
    if track is None or start is None or end is None or domain is None:return None
    return (track,start,end,timeline_domain_identity(domain))
def validate_placement_set(ps):
    # FR-13 construction invariant, consumed by EditPlanRevision.__post_init__ (and hence
    # new_revision) as well as check_no_overlap. T1 half-open intervals: [0,100)/[100,200)
    # are adjacent, not overlapping, so only b.start < a.end rejects.
    by={}
    for p in ps:
        iv=placement_interval(p)
        if iv is not None:by.setdefault(iv[0],[]).append(iv)
    for items in by.values():
        s=sorted(items,key=lambda x:x[1])
        for a,b in zip(s,s[1:]):
            if a[3]!=b[3]:raise ValueError("same-track placements are not in a comparable timeline domain")
            if b[1]<a[2]:raise ValueError("same-track placements overlap")
def check_no_overlap(ps):return validate_placement_set(ps)
