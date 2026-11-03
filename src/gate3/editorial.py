from dataclasses import dataclass,field
from pathlib import Path
class ModelToolPrincipalError(TypeError):pass
# Fixture-/filler-addressed principals can never confer real authority (R-15.b.4). This set
# mirrors, by local definition, ``plan.py``'s ``_FIXTURE_REF_PREFIXES`` for the same purpose;
# it is deliberately NOT imported from ``plan.py`` because ``plan.py`` imports this module and
# the import back would create a cycle.
_FIXTURE_PRINCIPAL_PREFIXES=("fixture:","fixture://","SYNTHETIC_FIXTURE")
@dataclass(frozen=True)
class EditorialDecision:
    decision_id:str; principal_kind:str; principal_ref:str; decided_on_refinement:str; decided_on_revision:int; decision_class:str; rationale:str; options_considered:list=field(default_factory=list); presentation_manifest_ref:str|None=None; accepted_sub_interval_ref:str|None=None; requested_modification:str|None=None; fixture_scope:str|None=None
    def __post_init__(self):
        if self.principal_kind not in ("human","SYNTHETIC_HUMAN"):raise ModelToolPrincipalError("model/tool principal cannot decide")
        if not self.rationale:raise ValueError("rationale mandatory")
        if self.decision_class not in ("ACCEPT","REJECT","MODIFY"):raise ValueError("invalid decision_class")
    @property
    def requested_modification_is_measurement(self):return False
    @property
    def principal_authority_evidence(self):
        """Evidence-backed real-principal authority, or None (Spec §20.4).

        NOT_OBSERVED at the current Gate-3 maturity: no principal registry or attestation
        capability is authorized.  A bare ``principal_ref`` string, a ``principal_kind``
        declaration, or a non-fixture prefix is NOT evidence and never satisfies this.
        """
        return None
    @property
    def real_authority_eligible(self):return self.principal_kind=="human" and self.fixture_scope is None and isinstance(self.principal_ref,str) and not self.principal_ref.startswith(_FIXTURE_PRINCIPAL_PREFIXES)
    def to_record(self):
        r={"decision_id":self.decision_id,"principal_kind":self.principal_kind,"principal_ref":self.principal_ref,"decided_on_refinement":self.decided_on_refinement,"decided_on_revision":self.decided_on_revision,"decision_class":self.decision_class,"rationale":self.rationale,"options_considered":list(self.options_considered)}
        for k in ("presentation_manifest_ref","accepted_sub_interval_ref","requested_modification","fixture_scope"):
            v=getattr(self,k)
            if v is not None:r[k]=v
        return r


def resolve_editorial_resume(bundle_path, decision_paths):
    """Resolve the one current human-decision head without mutating sealed artifacts."""
    from vip_fvs.human_decision import resolve_human_decision_resume

    if isinstance(decision_paths, (str, Path)):
        root = Path(decision_paths)
        paths = sorted(root.glob("*.json")) if root.is_dir() else [root]
    else:
        paths = list(decision_paths)
    return resolve_human_decision_resume(bundle_path, paths)
