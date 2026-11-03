from gate3.pts import PtsTable
RETENTION="RETENTION"
class FrameOrdinalBasis:
    def __init__(self,table:PtsTable,*,dedupe_policy:str,ordering:str="presentation"):
        if dedupe_policy!=RETENTION: raise ValueError("only RETENTION is the normative basis")
        if ordering!="presentation": raise ValueError("a decode-order ordinal may never populate source_frame")
        self.table=table; self.dedupe_policy=dedupe_policy; self.ordering=ordering
    def ordinal_to_tick(self,ordinal):
        if not isinstance(ordinal,int) or isinstance(ordinal,bool) or ordinal<0 or ordinal>=self.count():
            raise ValueError("retained presentation ordinal outside the enumerated basis")
        return self.table.ticks[ordinal]
    def count(self): return len(self.table.ticks)
    def ordinals_of(self,tick): return self.table.ordinals_of(tick)
    def is_retained_ordinal(self,ordinal): return isinstance(ordinal,int) and not isinstance(ordinal,bool) and 0<=ordinal<self.count()
    def basis(self): return {"ordering":self.ordering,"dedupe_policy":self.dedupe_policy}
def dts_evidence_required(*,has_b_frames:int,pts_equals_dts:bool): return has_b_frames>0 or not pts_equals_dts
