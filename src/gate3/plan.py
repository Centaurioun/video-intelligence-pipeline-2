from __future__ import annotations
from collections.abc import Mapping
from dataclasses import dataclass,field
from types import MappingProxyType
import copy,hashlib,json,re
from gate3.editorial import EditorialDecision
from gate3.placement import validate_placement_set
# FR-11 + the FX-2 owner ruling: the plan chain consumes *authoritatively* binding-eligible
# refinements. `is_binding_eligible` requires the FR-01 byte-bound evidence and re-measures the
# byte source the C2 entry names; a merely structural (shape-only) declaration must never be
# pinned. `is_structurally_eligible` is deliberately not imported here.
from gate3.refinement import is_binding_eligible

# ``supersedes`` must name a prior revision **digest** (R-09.c). A digest is lowercase hex;
# any non-digest claim (e.g. a free-form label) is rejected before the prior-revision identity
# is compared, and when prior-revision evidence is supplied the digest must match it exactly.
_DIGEST_SHAPE=re.compile(r"\A[0-9a-f]+\Z")
# Identifiers that can never authorize production export (contract §2 synthetic/fixture rule).
_FIXTURE_REF_PREFIXES=("fixture:","fixture://","SYNTHETIC_FIXTURE")

def _freeze(value):
    """Recursively copy ``value`` into immutable containers, leaving no caller alias."""
    if isinstance(value,Mapping):return MappingProxyType({k:_freeze(v) for k,v in dict(value).items()})
    if isinstance(value,(list,tuple)):return tuple(_freeze(v) for v in value)
    return copy.deepcopy(value)

def _thaw(value):
    """Return a fresh mutable deep copy so ``to_record()`` never leaks live internal state."""
    if isinstance(value,Mapping):return {k:_thaw(v) for k,v in dict(value).items()}
    if isinstance(value,(list,tuple)):return [_thaw(v) for v in value]
    return copy.deepcopy(value)

def _decision_projection(v):
    f=getattr(v,"to_record",None);return f() if callable(f) else v
def _placement_id_projection(entry):
    """Project one placement to its placement-id STRING for the emitted A.6 record.

    Appendix A.6 is frozen normative authority and types ``edit_plan_revision.placements`` as
    ``{"type":"array","items":{"type":"string"}}`` (implementation plan line 7957); A.7 owns the
    full timeline-interval record. The plan's INTERNAL ``placements`` therefore stay the full L4
    records -- FR-13 same-track no-overlap is enforced over them in ``__post_init__`` and
    ``placement.placement_interval`` returns ``None`` for a bare id string, so an id-only internal
    representation would make FR-13 vacuous. Only the EMITTED record is projected: a
    ``TimelinePlacement`` contributes its ``placement_id`` attribute, a mapping its
    ``placement_id`` key, and a bare string passes through unchanged.
    """
    if isinstance(entry,str):return entry
    pid=entry.get("placement_id") if isinstance(entry,Mapping) else getattr(entry,"placement_id",None)
    if not isinstance(pid,str) or not pid:raise ValueError("placement must carry a non-empty placement_id to be emitted in the A.6 record")
    return pid
@dataclass(frozen=True)
class EditPlanRevision:
    plan_id:str; plan_revision:int; placements:list; pinned_refinements:dict; pinned_decisions:dict; source_revision_ids:list=field(default_factory=list); supersedes:str|None=None; derived_from_refs:list=field(default_factory=list); plan_scope:str="REAL"; policy_decision_ref:str|None=None; prior_revision:object|None=None; pinned_evidence_digests:dict=field(default_factory=dict)
    def __post_init__(self):
        object.__setattr__(self,"placements",_freeze(self.placements));object.__setattr__(self,"source_revision_ids",_freeze(self.source_revision_ids));object.__setattr__(self,"derived_from_refs",_freeze(self.derived_from_refs));object.__setattr__(self,"pinned_refinements",_freeze(self.pinned_refinements));object.__setattr__(self,"pinned_decisions",_freeze(self.pinned_decisions))
        # Spec §16: the authority pin map is (refinement_id -> evidence_digest). ``None`` is the
        # legacy/absent spelling and normalizes to the empty map so every consumer below sees a
        # ``Mapping``; a non-mapping is refused outright rather than silently degraded.
        if self.pinned_evidence_digests is None:object.__setattr__(self,"pinned_evidence_digests",_freeze({}))
        elif isinstance(self.pinned_evidence_digests,Mapping):object.__setattr__(self,"pinned_evidence_digests",_freeze(self.pinned_evidence_digests))
        else:raise ValueError("pinned_evidence_digests must be a mapping of refinement_id to evidence_digest")
        # FR-13 construction invariant: same-track no-overlap is enforced here rather than
        # left to an optional caller-side helper, so a plan carrying overlapping same-track
        # placements cannot be constructed at all (new_revision routes through this too).
        validate_placement_set(self.placements)
        if self.plan_scope not in ("REAL","SYNTHETIC_FIXTURE"):raise ValueError("invalid plan_scope")
        if not self.pinned_refinements:raise ValueError("must pin refinement")
        if self.supersedes is not None:
            if not isinstance(self.supersedes,str) or not _DIGEST_SHAPE.match(self.supersedes):raise ValueError("supersedes must name a prior revision digest")
            if self.prior_revision is not None and self.supersedes!=getattr(self.prior_revision,"digest",None):raise ValueError("supersedes must equal the prior revision digest")
        for rid,ref in self.pinned_refinements.items():
            if not isinstance(ref,Mapping):raise ValueError("refinement record must be a mapping")
            if not is_binding_eligible(dict(ref)):raise ValueError("not an authoritatively binding-eligible gate3 refinement (FR-01 byte-bound evidence required)")
            if ref.get("refinement_id")!=rid:raise ValueError("refinement key must equal refinement_id")
            source_revision_id=ref.get("source_revision_id")
            # FR-11 exact cross-link (contract §4 FR-11 :117-118). For the AUTHORITATIVE plan scope
            # (``REAL`` -- the only scope §2 lets carry real editorial authority) the declared source
            # revision must be a non-empty string that IS listed. A missing/empty/None declared id
            # and an empty declared set are both "the link is absent", never "the link is exempt":
            # the old `if source_revision_id and self.source_revision_ids` double conjunct turned a
            # MISSING link into an EXEMPT one. The ``isinstance`` guard stops a non-string (e.g.
            # ``None``) from being carried as a "listed" value. SYNTHETIC_FIXTURE structural records
            # stay a distinct non-authoritative category (contract §2 :39-40) that may omit the set;
            # a non-empty mismatch still rejects on every scope (frozen FR-11 negative).
            if self.plan_scope=="REAL":
                if not isinstance(source_revision_id,str) or not source_revision_id.strip():
                    raise ValueError("an authoritative plan refinement must declare a non-empty source_revision_id")
                if not isinstance(self.source_revision_ids,(list,tuple)) or not any(isinstance(s,str) and s==source_revision_id for s in self.source_revision_ids):
                    raise ValueError("refinement source revision must be listed in source_revision_ids")
            elif source_revision_id and self.source_revision_ids and source_revision_id not in self.source_revision_ids:raise ValueError("refinement source revision must be listed in source_revision_ids")
            d=self.pinned_decisions.get(rid)
            if not isinstance(d,EditorialDecision):raise ValueError("must pin EditorialDecision")
            if d.decided_on_refinement!=rid:raise ValueError("pinned decision must be decided on its pinned refinement")
            if not 1<=d.decided_on_revision<=self.plan_revision:raise ValueError("pinned decision must name an existing plan revision")
            if self.plan_scope=="REAL" and not d.real_authority_eligible:raise ValueError("real plan requires real human")
            if self.plan_scope=="SYNTHETIC_FIXTURE" and not (d.principal_kind=="SYNTHETIC_HUMAN" and d.fixture_scope=="SYNTHETIC_FIXTURE"):raise ValueError("fixture plan requires synthetic fixture decision")
            # Spec §16: an authority pin is (refinement_id, evidence_digest).  A structural id
            # alone cannot distinguish same-ID/different-evidence substitution (ADJ-1).  ``ref``
            # is already frozen to a ``MappingProxyType`` by ``_freeze`` above, so the evidence
            # identity is read through the ``Mapping`` protocol rather than a concrete ``dict``.
            declared=self.pinned_evidence_digests.get(rid)
            actual=ref.get("evidence_digest") if isinstance(ref,Mapping) else None
            if not isinstance(actual,str) or not actual:
                raise ValueError("an authority-pinned refinement must carry evidence_digest")
            if declared is None:
                raise ValueError("an authority-pinned refinement requires a pinned evidence_digest")
            if declared!=actual:
                raise ValueError("pinned evidence_digest does not match the pinned refinement")
    @property
    def real_authority_eligible(self):return self.plan_scope=="REAL"
    @property
    def export_plan_structurally_valid(self):
        """STRUCTURAL export-plan validity ONLY (owner naming ruling, Spec §20.3).

        This answers whether the plan has a structurally valid shape for an export-plan workflow
        under the synthetic/current Gate-3 contract.  It does NOT imply real-human editorial
        authority, production authorization, actual export permission, or maturity promotion.
        It is a DIFFERENT property from ``export_eligible`` and must never be an alias of it.
        """
        if not isinstance(self.plan_id,str) or not self.plan_id.strip():return False
        if not isinstance(self.plan_revision,int) or isinstance(self.plan_revision,bool):return False
        if self.plan_revision<1:return False
        if self.plan_scope not in ("REAL","SYNTHETIC_FIXTURE"):return False
        if not isinstance(self.source_revision_ids,(list,tuple)) or not self.source_revision_ids:return False
        # ``__post_init__`` freezes both pinned mappings into ``MappingProxyType``, so the
        # structural predicate must test the ``Mapping`` protocol rather than the concrete
        # ``dict`` type (a ``dict`` test is always False here and would make this property
        # vacuously False, contradicting the owner ruling that a synthetic structural plan is
        # ``export_plan_structurally_valid is True``).
        if not isinstance(self.pinned_refinements,Mapping) or not self.pinned_refinements:return False
        if not isinstance(self.pinned_decisions,Mapping) or not self.pinned_decisions:return False
        for rid in self.pinned_refinements:
            d=self.pinned_decisions.get(rid)
            if not isinstance(d,EditorialDecision):return False
            if d.decided_on_refinement!=rid:return False
        return True
    @property
    def export_eligible(self):
        """ACTUAL production/export authority ONLY (owner naming ruling, Spec §20.3).

        This is the authority-bearing projection.  At the current Gate-3 maturity real human
        editorial authority is NOT_OBSERVED and no evidence-backed principal-attestation
        capability exists, so ``real_authority_eligible`` is a caller declaration and CANNOT
        confer authority.  Therefore this MUST be False for every synthetic, fixture, structural
        or merely REAL-scoped record, and the bare-principal path must fail closed.

        The single admitted path is an evidence-backed principal authority object supplied by a
        separately authorized capability.  Until that capability exists, that path is UNREACHABLE
        by construction.  Hard-coding False is forbidden (R-15.b.6): the honest path must remain
        demonstrable the day the capability arrives.
        """
        if not self.export_plan_structurally_valid:return False
        authority_surface=self.policy_decision_ref
        if not isinstance(authority_surface,str) or not authority_surface.strip():return False
        pinned=self.pinned_decisions.get(authority_surface)
        if not isinstance(pinned,EditorialDecision):return False
        # An evidence-backed principal authority capability does not exist in this epoch, so no
        # EditorialDecision can satisfy this predicate.  This is a POSITIVE requirement, not a
        # blanket False: `principal_authority_evidence` is the capability boundary.
        return bool(getattr(pinned,"principal_authority_evidence",None))
    @property
    def digest(self):
        p=json.dumps({"plan_id":self.plan_id,"plan_revision":self.plan_revision,"plan_scope":self.plan_scope,"placements":_thaw(self.placements),"refs":{k:(v.get("refinement_id"),v.get("evidence_digest")) for k,v in self.pinned_refinements.items()},"decisions":{k:getattr(v,"decision_id",v) for k,v in self.pinned_decisions.items()},"sources":list(self.source_revision_ids),"supersedes":self.supersedes},sort_keys=True,default=str)
        return hashlib.sha256(p.encode()).hexdigest()
    def to_record(self):
        r={"plan_id":self.plan_id,"plan_revision":self.plan_revision,"digest":self.digest,"plan_scope":self.plan_scope,"real_authority_eligible":self.real_authority_eligible,"export_plan_structurally_valid":self.export_plan_structurally_valid,"export_eligible":self.export_eligible,"placements":[_placement_id_projection(p) for p in self.placements],"pinned_refinements":_thaw(self.pinned_refinements),"pinned_decisions":{k:_thaw(_decision_projection(v)) for k,v in self.pinned_decisions.items()},"pinned_evidence_digests":dict(self.pinned_evidence_digests),"source_revision_ids":list(self.source_revision_ids),"derived_from_refs":list(self.derived_from_refs)}
        if self.supersedes:r["supersedes"]=self.supersedes
        if self.policy_decision_ref:r["policy_decision_ref"]=self.policy_decision_ref
        return r
def new_revision(prev,*,placements,pinned_refinements,pinned_decisions,source_revision_ids=None,policy_decision_ref=None,pinned_evidence_digests=None):return EditPlanRevision(prev.plan_id,prev.plan_revision+1,placements,pinned_refinements,pinned_decisions,list(source_revision_ids if source_revision_ids is not None else prev.source_revision_ids),supersedes=prev.digest,derived_from_refs=[prev.digest],plan_scope=prev.plan_scope,policy_decision_ref=policy_decision_ref if policy_decision_ref is not None else prev.policy_decision_ref,prior_revision=prev,pinned_evidence_digests=dict(pinned_evidence_digests if pinned_evidence_digests is not None else prev.pinned_evidence_digests))
