from __future__ import annotations
from dataclasses import dataclass,field
from dataclasses import fields as dataclass_fields
from fractions import Fraction
import hashlib
HOP_SOURCE_PTS_TO_FRAME="source_pts_to_frame"; HOP_FRAME_TO_PROXY="frame_to_proxy"; HOP_PROXY_TO_TIMELINE="proxy_to_timeline"; HOP_TIMELINE_TO_RENDERED="timeline_to_rendered"
HOPS=(HOP_SOURCE_PTS_TO_FRAME,HOP_FRAME_TO_PROXY,HOP_PROXY_TO_TIMELINE,HOP_TIMELINE_TO_RENDERED)
METHOD_TOKENS=("identity","affine","frame_list","piecewise"); EXACTNESS_TOKENS=("exact","quantized","unverified")
AFFINE_METHODS=("identity","affine"); ENUMERABLE_METHODS=("frame_list","piecewise")
_AFFINE_KEYS=frozenset(("offset","scale_num","scale_den")); _OPTIONAL_PARAM_KEYS=frozenset(("tolerance",))
_SEGMENT_KEYS=("segments","samples")

def _is_int(v): return isinstance(v,int) and not isinstance(v,bool)

def _affine_transform(params):
    """Return (offset, scale) as Fractions for identity/affine, or None if not evaluable.

    An empty/absent mapping of the affine keys is the identity (R-06.d rule 1).
    """
    if not isinstance(params,dict): return None
    keys=set(params)
    if not keys: return (Fraction(0),Fraction(1))
    if not keys <= (_AFFINE_KEYS|_OPTIONAL_PARAM_KEYS): return None
    off=params.get("offset",0); sn=params.get("scale_num",1); sd=params.get("scale_den",1)
    if not all(_is_int(v) for v in (off,sn,sd)): return None
    if sd==0: return None
    return (Fraction(off),Fraction(sn,sd))

def _enumerable_transform(params):
    """Return the declared list of (src,dst) integer pairs, or None if not evaluable."""
    if not isinstance(params,dict): return None
    raw=None
    for key in _SEGMENT_KEYS:
        if key in params: raw=params[key]; break
    if not isinstance(raw,(list,tuple)) or len(raw)<2: return None
    out=[]
    for pair in raw:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2: return None
        a,b=pair
        if not (_is_int(a) and _is_int(b)): return None
        out.append((a,b))
    return out

def _deltas(sample):
    return [b-a for a,b in zip(sample,sample[1:])]

def _measured_residual(transform,sample,hop=None):
    """Sampled round-trip residual of the declared transform over the enumerated sample.

    Returns None when there is no evaluable transform or the sample cannot be measured.

    Two hop classes, both in exact-rational (Fraction) arithmetic:

    * ``source_pts_to_frame``: the enumerated sample is the source-PTS tick sequence and the true
      source-frame of the i-th sampled tick is its presentation ordinal ``i`` (FR-02/T4; stated in
      ``tests/gate3/test_fr04_mapping_authority.py``). The sampled round trip is therefore the
      declared transform applied to each sampled tick against that ordinal:
      ``sum_i |offset + scale*sample_i - i|``. A non-unit affine scale, a non-zero offset, or a
      non-uniform enumeration is measurably non-zero -- FX-3: ``2/1`` over ``(0,1,2)`` measures 3.
    * every other hop: the enumerated sample is already a lattice in the transform's own domain, so
      the residual is the integrality deviation of the transform over the enumerated ticks plus the
      non-uniformity of that enumeration. Identity over ANY uniformly spaced enumeration measures
      zero there, which is what FR-15 a5's ``(0,10)`` and the render chain's ``(0,50)`` require.
    """
    if transform is None: return None
    if len(sample)<2: return None
    kind,payload=transform
    if kind=="affine":
        off,scale=payload; sn=scale.numerator; sd=scale.denominator
        if hop==HOP_SOURCE_PTS_TO_FRAME:
            # FR-04 data model: the i-th enumerated source tick's true frame is ordinal i.
            return sum(abs(off+scale*p-i) for i,p in enumerate(sample))
        # Exact-rational ELIGIBILITY: the transform must map every sampled integer to an integer,
        # so a non-integral scale (e.g. 1/2) is ineligible over an integer enumeration.
        # MEASURED residual combines two independent non-zero sources:
        #  (i) integrality deviation -- a non-integral scale (e.g. 1/2) cannot map an integer
        #      enumeration to integers, so the exact-rational round-trip cannot be zero; this stays
        #      BOUNDABLE, so a declared bound that admits it is quantized (FR-04 RED-8) while a zero
        #      declared bound is unverified (FR-04 RED-3);
        #  (ii) non-uniformity of the enumeration -- an identity/affine transform is exact over ANY
        #      uniformly spaced sample (FR-15 a5 uses (0,10)) and inexact over a non-uniform one
        #      (FR-04 RED-2 uses (0,1000,1250)).
        integrality=sum(abs((x*sn)%sd) for x in sample)
        delta=_deltas(sample)
        if not delta:return None
        first=delta[0]
        return integrality+sum(abs(d-first) for d in delta)
    pairs=payload; total=0
    declared=_deltas([s for s,_ in pairs])
    observed=_deltas(sample)
    n=min(len(declared),len(observed))
    if n==0: return None
    for i in range(n): total+=abs(declared[i]-observed[i])
    total+=abs(len(declared)-len(observed))
    return total

def _parse(params,method):
    if method in AFFINE_METHODS:
        t=_affine_transform(params)
        return None if t is None else ("affine",t)
    if method in ENUMERABLE_METHODS:
        t=_enumerable_transform(params)
        return None if t is None else ("enumerable",t)
    return None

def _exact_eligible(transform):
    """T10 first clause: exact-rational transform eligibility for `exact`.

    An affine transform is eligible only when its scale is an integer, so every integer enumerated
    tick maps to an integer target tick. A non-integral scale (e.g. 1/2) stays EVALUABLE and
    BOUNDABLE -- so a declared bound that admits its measured round trip is still `quantized`
    (FR-04 RED-8) -- but it can never be `exact` over an integer enumeration, even when that
    particular enumeration happens to land on integers (FX-3: 1/2 over (0,2,4)).
    """
    if transform is None: return False
    kind,payload=transform
    if kind=="affine":
        _off,scale=payload
        return scale.denominator==1
    return True

def _computed_status(m):
    """T10: exactness is computed from transform eligibility AND a measured zero residual."""
    if m.residual is None: return "unverified"
    if not m.validated_sample: return "unverified"
    transform=_parse(m.params,m.method)
    measured=_measured_residual(transform,m.validated_sample,m.hop)
    if measured is None: return "unverified"
    if measured==0 and m.residual==0:
        # A caller-declared zero residual cannot manufacture `exact` unless the transform is itself
        # exact-rational eligible (T10). An ineligible transform with no measurable non-zero
        # residual has nothing admissible to quantize, so it is `unverified`, never binding.
        return "exact" if _exact_eligible(transform) else "unverified"
    if abs(m.residual)>=abs(measured): return "quantized"
    return "unverified"

@dataclass(frozen=True)
class MappingArtifact:
    mapping_id:str; artifact_type:str; digest:str; parents:tuple[str,...]; retention:str; availability:str; hop:str; method:str; params:dict; validated_sample:tuple[int,...]; residual:int|None; producer_attempt_id:str|None=None; reconstruction:bool=False; digest_algorithm:str="sha256"; parent_artifact_digest:str|None=None; derivations:tuple[str,...]=field(default_factory=tuple); exactness:str|None=None
    def __post_init__(self):
        if self.hop not in HOPS: raise ValueError("unknown hop")
        if self.artifact_type!="mapping_artifact": raise ValueError("artifact_type must be mapping_artifact")
        if not self.digest or not self.parents or not self.retention or not self.availability or not self.producer_attempt_id: raise ValueError("mapping provenance incomplete")
        if self.method not in METHOD_TOKENS: raise ValueError("invalid method")
        # A caller-declared exactness token is validated for shape but NEVER decides the status (T10).
        if self.exactness is not None and self.exactness not in EXACTNESS_TOKENS: raise ValueError("invalid exactness")
        if not all(isinstance(x,int) and not isinstance(x,bool) for x in self.validated_sample): raise ValueError("validated_sample must be integers")
        if self.residual is not None and (not isinstance(self.residual,int) or isinstance(self.residual,bool)): raise ValueError("residual must be int or None")
    @property
    def mapping_form(self): return "affine" if self.method in AFFINE_METHODS else "piecewise_segments"
    @property
    def computed_exactness(self): return _computed_status(self)
    def to_record(self): return {"mapping_id":self.mapping_id,"artifact_type":self.artifact_type,"digest":self.digest,"parents":list(self.parents),"producer_attempt_id":self.producer_attempt_id,"retention":self.retention,"availability":self.availability,"hop":self.hop,"method":self.method,"mapping_form":self.mapping_form,"params":dict(self.params) if isinstance(self.params,dict) else self.params,"exactness":self.computed_exactness,"validated_sample":list(self.validated_sample),"residual":self.residual,"reconstruction":self.reconstruction}
    def may_support_binding(self): return not self.reconstruction and self.computed_exactness in ("exact","quantized")

class _RecordEvidence:
    """Attribute view over a mapping RECORD so the FR-04 authority can recompute T10 status.

    ``_computed_status`` reads attributes; this explicit, symmetric conversion lets a persisted
    mapping record (``MappingArtifact.to_record()`` shape) be re-verified by the same authority
    that verifies the typed artifact, instead of raising ``AttributeError``.
    """
    __slots__=("hop","method","params","validated_sample","residual")
    def __init__(self,record):
        self.hop=record.get("hop");self.method=record.get("method");self.params=record.get("params")
        self.validated_sample=record.get("validated_sample");self.residual=record.get("residual")


def validate_hop(m):
    """T10 status: recomputed from transform evidence, never read from a declared token.

    Total over the typed artifact, a persisted record and any other object exposing the FR-04
    evidence attributes: an unreadable/ill-typed input recomputes to ``unverified`` (fail closed),
    it never raises.
    """
    try:
        if isinstance(m,MappingArtifact): return m.computed_exactness
        if isinstance(m,dict): return _computed_status(_RecordEvidence(m))
        return _computed_status(m)
    except Exception:
        return "unverified"


# The provenance header Spec §11.1 requires a consumer to READ (the GEN2-BLK-3 defect was that
# the FR-12 consumer read none of it).
_MAPPING_PROVENANCE_HEADER=("mapping_id","artifact_type","digest","parents","producer_attempt_id",
                            "retention","availability")


def _as_artifact_record(m):
    """Explicit, symmetric conversion between the typed artifact and its persisted record.

    A ``MappingArtifact`` projects to its record (optional coordinate-domain pair preserved when
    the object carries it); a mapping record is used as-is; anything else has no artifact origin.
    """
    if isinstance(m,MappingArtifact):
        record=m.to_record()
        for field in ("from_domain","to_domain"):
            value=getattr(m,field,None)
            if value is not None:record[field]=value
        return record
    if isinstance(m,dict): return m
    return None


def _rebuild_artifact(record):
    """Re-derive the typed artifact from a record, or ``None`` when the record is not one.

    This is the record -> artifact half of the symmetric conversion: the dataclass' own
    ``__post_init__`` re-validates hop/method/params/sample/residual types and provenance
    completeness, so a malformed or non-artifact record fails closed here.
    """
    if not isinstance(record,dict):return None
    known={f.name for f in dataclass_fields(MappingArtifact)}
    kwargs={}
    for name in known:
        if name not in record:continue
        value=record[name]
        if name in ("parents","validated_sample","derivations") and isinstance(value,list):
            value=tuple(value)
        kwargs[name]=value
    try:
        return MappingArtifact(**kwargs)
    except Exception:
        return None


def mapping_evidence_digest(m) -> "str | None":
    """The mapping artifact's evidence identity (Spec §15.2/§15.3).

    The artifact's EXISTING ``digest`` field IS its ``evidence_digest`` — one digest, not two.
    Authority consumers recompute it over the artifact's own transform evidence, so custody
    metadata (parents/producer_attempt_id/retention/availability/artifact_type) and the
    recomputed ``exactness`` token are excluded.
    """
    from gate3 import authority
    record=_as_artifact_record(m)
    if record is None:return None
    try:
        return authority.evidence_digest(authority.RECORD_KIND_MAPPING,record)
    except Exception:
        return None


def mapping_identity_address(mapping_id) -> "str | None":
    """The artifact's identity address: ``sha256(mapping_id)`` (Spec §11.1 "Artifact identity")."""
    if not isinstance(mapping_id,str) or not mapping_id.strip():return None
    return hashlib.sha256(mapping_id.encode("utf-8")).hexdigest()


def _declared_status_agrees(record,artifact) -> bool:
    """Tamper evidence: a persisted derived status token must not contradict recomputation.

    The token is never *trusted* as authority (§15.4.2: it is excluded from the digest and always
    recomputed).  A record whose persisted ``exactness`` disagrees with the status recomputed from
    its own transform evidence is evidence that the artifact was edited after production, so it is
    refused (fail closed).
    """
    declared=record.get("exactness")
    if declared is None:return True
    return declared==artifact.computed_exactness


def _digest_names_the_artifact(record,declared) -> bool:
    """The declared digest must be a re-derivable identity of THIS artifact.

    Exactly two forms are accepted, and both are RE-DERIVED here rather than trusted:

    1. the recomputed evidence identity ``mapping_evidence_digest(record)`` — the canonical
       projection of this artifact's own transform evidence (Spec §15.2/§15.3; "one digest, not
       two"), which excludes the declared ``digest`` field and the recomputed ``exactness`` token;
       or
    2. the artifact's identity address ``mapping_identity_address(mapping_id)`` =
       ``sha256(mapping_id)`` (Spec §11.1 "Artifact identity").

    Nothing else is accepted.  In particular a declared value that merely CONTAINS the
    ``mapping_id`` — e.g. the pre-evidence-identity ``digest-<mapping_id>`` label — is a
    string-shape heuristic, not an identity, and is refused; so is any 64-hex value that is
    neither form (a forged digest) and any absent/ill-typed value.

    Residual (recorded deliberately, not overclaimed).  Form (2) is an identity ADDRESS, not an
    evidence commitment: an artifact can declare ``sha256(mapping_id)`` and still carry arbitrary
    transform evidence, so this predicate alone does not bind the evidence a consumer relies on.
    The residual is mitigated where the predicate is actually consumed: the FR-12 consumer
    ``_mapping_proof`` independently recomputes the T10/exactness status from the record's own
    transform evidence and always EMITS the recomputed evidence digest (Spec §11.3), so a form-(2)
    artifact cannot license a relation it has not evidenced.  Separately, the frozen production
    producer ``src/gate3/render_adapter.py`` stores the rendered-output BYTE digest in this field,
    which satisfies NEITHER accepted form; that is not a production regression because the render
    chain's mapping is never passed to this consumer (verified by grep), and a later authorized
    epoch may align the producer to emit the evidence projection.
    """
    evidence=mapping_evidence_digest(record)
    if isinstance(evidence,str) and evidence and declared==evidence:return True
    return declared==mapping_identity_address(record.get("mapping_id"))


def mapping_is_attributable(m) -> bool:
    """True only when the mapping carries the required provenance header AND a recomputed digest.

    Spec §11.1: the artifact must be readable AS an artifact — identity, artifact type, producer
    attempt, non-empty parent bindings, retention/availability and a digest that is re-derivable
    from the artifact itself — and it must be re-derivable as a shape-valid ``MappingArtifact``.
    A caller-authored scalar mapping record has no artifact origin and is refused.
    """
    record=_as_artifact_record(m)
    if record is None:return False
    try:
        for field in _MAPPING_PROVENANCE_HEADER:
            if not record.get(field):return False
        if record.get("artifact_type")!="mapping_artifact":return False
        mapping_id=record.get("mapping_id")
        if not isinstance(mapping_id,str) or not mapping_id.strip():return False
        parents=record.get("parents")
        if not isinstance(parents,(list,tuple)) or not parents:return False
        if not all(isinstance(p,str) and p.strip() for p in parents):return False
        artifact=_rebuild_artifact(record)
        if artifact is None:return False
        if not _declared_status_agrees(record,artifact):return False
        declared=record.get("digest")
        if not isinstance(declared,str) or not declared.strip():return False
        return _digest_names_the_artifact(record,declared)
    except Exception:
        return False
