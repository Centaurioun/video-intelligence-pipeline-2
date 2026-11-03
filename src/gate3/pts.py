from __future__ import annotations
from dataclasses import dataclass
from bisect import bisect_left,bisect_right
from gate3.rational import TimeBase

@dataclass(frozen=True)
class PtsTable:
    time_base:TimeBase
    ticks:tuple[int,...]
    def __post_init__(self):
        if not self.ticks: raise ValueError("PTS table must not be empty")
        if any(not isinstance(t,int) or isinstance(t,bool) for t in self.ticks): raise ValueError("PTS ticks must be integers")
        if any(b<a for a,b in zip(self.ticks,self.ticks[1:])): raise ValueError("presentation PTS must be non-decreasing")
    def contains(self,tick): return tick in self.ticks
    def first_at_or_after(self,tick):
        i=bisect_left(self.ticks,tick); return self.ticks[i] if i<len(self.ticks) else None
    def first_strictly_after(self,tick):
        i=bisect_right(self.ticks,tick); return self.ticks[i] if i<len(self.ticks) else None
    def covering_tick(self,tick):
        i=bisect_right(self.ticks,tick); return self.ticks[i-1] if i>0 else None
    def ordinals_of(self,tick):
        """Every retained ordinal whose presentation PTS equals ``tick`` (occurrence-aware).

        T2 retains duplicate presentation PTS, so a tick may map to more than one retained
        ordinal; a silent first-match collapse would merge distinct frames.
        """
        return tuple(i for i,t in enumerate(self.ticks) if t==tick)
    def is_ambiguous(self,tick): return len(self.ordinals_of(tick))>1
    def ordinal_of(self,tick,*,occurrence=None):
        """Resolve ``tick`` to a retained ordinal; refuse an ambiguous collapse.

        ``occurrence=None`` returns the ordinal only when the tick is retained exactly once.
        Otherwise the caller must state which retained occurrence it means.
        """
        hits=self.ordinals_of(tick)
        if not hits: return None
        if occurrence is None:
            if len(hits)>1: raise ValueError("presentation PTS is retained more than once; occurrence required")
            return hits[0]
        if not isinstance(occurrence,int) or isinstance(occurrence,bool) or occurrence<0 or occurrence>=len(hits): return None
        return hits[occurrence]
    def is_boundary_member(self,tick): return self.contains(tick)
