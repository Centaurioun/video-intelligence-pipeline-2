"""T1–T11 temporal semantics. Exact rational, source-native, no nominal-FPS frame inference."""
from __future__ import annotations
from dataclasses import dataclass
from gate3.pts import PtsTable
from gate3.rational import Rational,TimeBase

@dataclass(frozen=True)
class SnapResult:
    requested_ticks:int; resolved_ticks:int|None; policy:str

def resolve_start(table,requested_ticks): return SnapResult(requested_ticks,table.first_at_or_after(requested_ticks),"first_pts_at_or_after")
def resolve_end(table,requested_ticks): return SnapResult(requested_ticks,table.first_strictly_after(requested_ticks),"first_pts_strictly_after")

PRECISION_TO_DOMAIN={"semantic-window":"semantic_seconds","source-pts":"source_pts","source-frame":"source_frame","timeline-rational":"timeline_time","rendered-output":"rendered_output"}
PRECISION_TOKENS=tuple(PRECISION_TO_DOMAIN)
def validate_precision(token):
    if token not in PRECISION_TO_DOMAIN: raise ValueError(f"unknown Gate-3-local precision token: {token!r}")
    return token

def _within_one_tick(a,b): return abs(a.numerator*b.denominator-b.numerator*a.denominator)<=a.denominator*b.denominator
def _declared_period_in_ticks(rate,tb): return Rational(rate.denominator,rate.numerator)*Rational(tb.den,tb.num)
def classify_vfr(table,declared_rate=None):
    ticks=table.ticks; n=len(ticks)
    if n<2: return ("unknown",None,"insufficient_sequence",None)
    p_measured=Rational(ticks[-1]-ticks[0],n-1); p,basis,deviation=p_measured,"measured_span",None
    if declared_rate is not None:
        p_declared=_declared_period_in_ticks(declared_rate,table.time_base)
        if _within_one_tick(p_declared,p_measured): p,basis=p_declared,"declared_rate_confirmed"
        else: deviation={"kind":"DECLARED_RATE_INCONSISTENT_WITH_ENUMERATED_SEQUENCE","declared_period_ticks":f"{p_declared.numerator}/{p_declared.denominator}","measured_period_ticks":f"{p_measured.numerator}/{p_measured.denominator}","governing_basis":"measured_span"}
    deltas=[b-a for a,b in zip(ticks,ticks[1:])]
    return ("false" if all(_within_one_tick(Rational(d,1),p) for d in deltas) else "true",p,basis,deviation)

@dataclass(frozen=True)
class TailEnd:
    end_ticks:int|None; end_is_stream_tail:bool; extent_state:str; binding_eligible:bool; derivation:str|None=None

def tail_end(table,*,container_facts=None,last_delta_ticks=None,rate_regime=None):
    last=table.ticks[-1]
    if container_facts is not None:
        nb=container_facts.get("nb_frames"); dur=container_facts.get("duration_ts")
        if nb is None or dur is None: raise ValueError("container facts must include nb_frames and duration_ts")
        if nb!=len(table.ticks): raise ValueError("nb_frames is inconsistent with enumerated PTS")
        consistency=container_facts.get("duration_consistency")
        if consistency is not None and consistency!="MATCH": return TailEnd(None,True,"UNCERTAIN",False,None)
        if dur<=last: raise ValueError("duration_ts does not extend beyond the last PTS")
        return TailEnd(dur,True,"DERIVED_NOT_OBSERVED",True,"duration_ts - last_pts")
    if last_delta_ticks is not None:
        if rate_regime!="uniform": raise ValueError("last-delta tail extent requires recorded uniform regime")
        return TailEnd(last+last_delta_ticks,True,"DERIVED_NOT_OBSERVED",True,"last_pts + uniform_delta")
    return TailEnd(None,True,"UNCERTAIN",False,None)

@dataclass(frozen=True)
class Interval:
    interval_id:str; time_domain:str; start_ticks:int; end_ticks:int; endpoint_semantics:str; end_is_stream_tail:bool; precision:str; last_frame_extent:int|None=None
    def __post_init__(self):
        if self.endpoint_semantics!="half_open": raise ValueError("only half-open endpoint semantics are admissible")
        validate_precision(self.precision)
    @property
    def duration_ticks(self): return duration_ticks(self)
def duration_ticks(interval):
    if interval.end_ticks<=interval.start_ticks: raise ValueError("interval must satisfy start < end")
    return interval.end_ticks-interval.start_ticks

DISCONTINUITY_GAP_MULTIPLE=3
def detect_discontinuity(table,start_ticks,end_ticks):
    ticks=[t for t in table.ticks if start_ticks<=t<=end_ticks]
    if len(ticks)<2: return []
    deltas=[b-a for a,b in zip(ticks,ticks[1:])]; ordered=sorted(deltas); n=len(ordered)
    median=ordered[n//2] if n%2 else (ordered[n//2-1]+ordered[n//2])//2
    if median<=0: return []
    threshold=DISCONTINUITY_GAP_MULTIPLE*median
    return [(a,b) for a,b in zip(ticks,ticks[1:]) if b-a>threshold]
def subdivide_on_discontinuity(table,start_ticks,end_ticks):
    gaps=detect_discontinuity(table,start_ticks,end_ticks)
    if not gaps: return ((start_ticks,end_ticks),),[]
    parts=[]; cursor=start_ticks
    for a,b in gaps:
        if cursor<a: parts.append((cursor,a))
        cursor=b
    if cursor<end_ticks: parts.append((cursor,end_ticks))
    return tuple(parts),gaps
