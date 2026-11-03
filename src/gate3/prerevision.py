from __future__ import annotations
from dataclasses import dataclass
import hashlib
@dataclass(frozen=True)
class PreRevisionRecord:
    record_id:str; occurrence_ref:str; revision_resolution:str="PENDING"; interval:None=None; source_revision_id:None=None; supersedes:None=None
    def __post_init__(self):
        if not self.occurrence_ref or self.revision_resolution!="PENDING": raise ValueError("pre-revision record must be pending with occurrence ref")
        if self.interval is not None or self.source_revision_id is not None: raise ValueError("pre-revision record carries no interval or revision id")
    @property
    def refinement_eligible(self): return False
    def to_record(self): return {"record_id":self.record_id,"occurrence_ref":self.occurrence_ref,"revision_resolution":"PENDING","interval":None,"source_revision_id":None,"supersedes":None}
@dataclass(frozen=True)
class ResolvedInterval:
    record_id:str; source_revision_id:str; supersedes:str; occurrence_ref:str; interval_ref:str; revision_resolution:str="RESOLVED"; endpoint_semantics:str="half_open"
    def __post_init__(self):
        if not self.source_revision_id or self.revision_resolution!="RESOLVED" or not self.interval_ref or self.endpoint_semantics!="half_open": raise ValueError("invalid resolved interval")
    @property
    def refinement_eligible(self): return True
    def to_candidate_fields(self): return {"source_revision_id":self.source_revision_id,"interval_id":self.interval_ref,"endpoint_semantics":self.endpoint_semantics,"evidence_assertion_refs":[self.supersedes,self.occurrence_ref]}
def resolve_prerevision(record,*,source_revision_id,supersedes,interval_ref):
    if not source_revision_id: raise ValueError("resolution must name source revision")
    if supersedes!=record.record_id: raise ValueError("resolution must supersede the pre-revision record it resolves")
    digest=hashlib.sha256(f"{source_revision_id}:{supersedes}".encode()).hexdigest()[:16]
    return ResolvedInterval(f"rev_{digest}",source_revision_id,supersedes,record.occurrence_ref,interval_ref)
