"""Typed Match comparability: a numeric coincidence is not a Match without a comparable space.

FR-12: numerically equal intervals in incompatible coordinate spaces must not become Match
relations without a validated mapping proof. Records that declare NO coordinate metadata share a
single legacy comparable space, so metadata-absent callers keep their previous behaviour.

FR-04 -> FR-12 (contract §6: "FR-04 precedes FR-12 and FR-15 mapping use"): a mapping licenses a
cross-space Match only when

* ``reconstruction is False``;
* its FR-04 status is RECOMPUTED from transform evidence to ``exact``/``quantized`` through the
  mapping authority's own ``validate_hop`` (never a caller-declared ``exactness`` token, never a
  bare mapping-like object carrying only the legacy truthy fields);
* it RESOLVES to an attributable mapping ARTIFACT (Spec §11.1: ``artifact_type``, ``mapping_id``,
  non-empty ``parents``, ``producer_attempt_id``, ``retention``, ``availability`` and a
  re-derivable ``digest``) — provenance is ADDITIONAL authority and never replaces the T10
  recomputation; the relation cites the recomputed ``evidence_digest`` of the mapping used; and
* its declared coordinate domain pair (``from_domain``/``to_domain`` when present, else derived from
  ``hop``) set-equals the two compared records' DIFFERING ``time_domain`` pair, so mere intersection
  with one side is not connection.

Every check fails closed and never propagates a caller object's exception.
"""
from __future__ import annotations
import json
from gate3.mapping import (
    HOPS,
    HOP_FRAME_TO_PROXY,
    HOP_PROXY_TO_TIMELINE,
    HOP_SOURCE_PTS_TO_FRAME,
    HOP_TIMELINE_TO_RENDERED,
    METHOD_TOKENS,
    MappingArtifact,
    mapping_evidence_digest,
    mapping_is_attributable,
    validate_hop,
)

SPACE_KEYS=("source_revision_id","stream_index","time_domain","time_base","time_base_or_rate")
NON_COMPARABILITY_TOKEN="NO_DETERMINATION"
BINDING_STATUSES=("exact","quantized")
# The two typed coordinate-domain endpoints each frozen hop relates (A.8 ``hop`` vocabulary).
HOP_DOMAINS={
    HOP_SOURCE_PTS_TO_FRAME:("source_pts","source_frame"),
    HOP_FRAME_TO_PROXY:("source_frame","proxy_time"),
    HOP_PROXY_TO_TIMELINE:("proxy_time","timeline_time"),
    HOP_TIMELINE_TO_RENDERED:("timeline_time","rendered_output"),
}


def coordinate_space_key(record):
    """Typed coordinate-space identity of a record (``"legacy"`` when it declares no metadata)."""
    parts=[]
    for key in SPACE_KEYS:
        value=record.get(key)
        if value is None:continue
        if isinstance(value,(dict,list,tuple)):
            value=json.dumps(value,sort_keys=True,default=str)
        parts.append(f"{key}={value}")
    return "|".join(parts) if parts else "legacy"


def _is_int(value):
    """Schema-integer test: ``bool`` is a subclass of ``int`` but never a valid tick/residual."""
    return isinstance(value,int) and not isinstance(value,bool)


def _mapping_fields(m):
    """Normalized transform-evidence view of a mapping record/artifact, or ``None``.

    Reads only the FR-04 fields plus ``reconstruction``, the declared domain pair and the reference.
    It never calls a caller-supplied method, so a dict subclass whose ``may_support_binding()``
    raises (or lies) cannot reach relation determination: the status is always recomputed by
    ``validate_hop`` from the evidence below.
    """
    try:
        if isinstance(m,MappingArtifact):
            return {"hop":m.hop,"method":m.method,"params":m.params,
                    "validated_sample":m.validated_sample,"residual":m.residual,
                    "reconstruction":m.reconstruction,
                    "from_domain":getattr(m,"from_domain",None),
                    "to_domain":getattr(m,"to_domain",None),
                    "ref":m.mapping_id}
        if isinstance(m,dict):
            ref=m.get("mapping_artifact_ref") or m.get("mapping_id")
            return {"hop":m.get("hop"),"method":m.get("method"),"params":m.get("params"),
                    "validated_sample":m.get("validated_sample"),"residual":m.get("residual"),
                    "reconstruction":m.get("reconstruction"),
                    "from_domain":m.get("from_domain"),"to_domain":m.get("to_domain"),
                    "ref":ref}
    except Exception:
        return None
    return None


def _transform_evidence_wellformed(fields):
    """Type gate before FR-04 recomputation: malformed scalar/container forms fail closed."""
    if fields["reconstruction"] is not False:return False
    if fields["hop"] not in HOPS:return False
    if fields["method"] not in METHOD_TOKENS:return False
    if not isinstance(fields["params"],dict):return False
    residual=fields["residual"]
    if residual is not None and not _is_int(residual):return False
    sample=fields["validated_sample"]
    if not isinstance(sample,(list,tuple)):return False
    if not all(_is_int(tick) for tick in sample):return False
    ref=fields["ref"]
    if not isinstance(ref,str) or not ref.strip():return False
    return True


class _MappingEvidence:
    """Attribute view so gate3.mapping's FR-04 authority recomputes status from evidence."""
    __slots__=("hop","method","params","validated_sample","residual")
    def __init__(self,fields):
        self.hop=fields["hop"];self.method=fields["method"];self.params=fields["params"]
        self.validated_sample=fields["validated_sample"];self.residual=fields["residual"]


def _record_domain(record):
    """The record's non-empty typed ``time_domain``, or ``None`` when it declares none."""
    try:
        domain=record.get("time_domain")
    except Exception:
        return None
    return domain if isinstance(domain,str) and domain.strip() else None


def _declared_domains(fields):
    """The mapping's declared domain pair: explicit ``from_domain``/``to_domain``, else ``hop``.

    A partially declared pair (exactly one of the two present) is malformed and yields ``None``.
    """
    from_domain=fields["from_domain"];to_domain=fields["to_domain"]
    if from_domain is None and to_domain is None:
        return HOP_DOMAINS.get(fields["hop"])
    if isinstance(from_domain,str) and from_domain.strip() and isinstance(to_domain,str) and to_domain.strip():
        return (from_domain,to_domain)
    return None


def _connects_spaces(fields,a,b):
    """True only when the mapping's declared pair set-equals the two DIFFERING record domains."""
    domain_a=_record_domain(a);domain_b=_record_domain(b)
    if domain_a is None or domain_b is None or domain_a==domain_b:return False
    declared=_declared_domains(fields)
    if declared is None:return False
    return set(declared)=={domain_a,domain_b}


def _mapping_proof(m,a,b):
    """A validated, ATTRIBUTABLE mapping artifact may license a cross-space comparison.

    FR-04/FR-12 predicate (Spec §11): the mapping must RESOLVE to an attributable artifact whose
    own evidence digest recomputes AND whose FR-04/T10 status recomputes to exact/quantized AND
    whose declared domain pair connects the two compared spaces.  Artifact provenance is
    ADDITIONAL admission authority; it never replaces T10 verification.  A bare scalar dict has
    no artifact origin and is refused.
    """
    try:
        fields=_mapping_fields(m)
        if fields is None:return None
        if not _transform_evidence_wellformed(fields):return None
        if not _connects_spaces(fields,a,b):return None
        if validate_hop(_MappingEvidence(fields)) not in BINDING_STATUSES:return None
        if not mapping_is_attributable(m):return None
        digest=mapping_evidence_digest(m)
        if not isinstance(digest,str) or not digest:return None
        ref=fields["ref"]
        return {"mapping_artifact_ref":ref,"mapping_id":ref,"evidence_digest":digest}
    except Exception:
        return None


def _licensing_proof(a,b,mappings):
    ka=coordinate_space_key(a);kb=coordinate_space_key(b)
    if ka==kb:return ka
    for m in mappings or ():
        proof=_mapping_proof(m,a,b)
        if proof is None:continue
        return proof
    return None


def determine_relations(records,mappings=None):
    records=list(records);mappings=list(mappings or ())
    relations=[];non_comparable=False
    for i,a in enumerate(records):
        for b in records[i+1:]:
            proof=_licensing_proof(a,b,mappings)
            if proof is None:
                # No comparable space and no validated mapping: record non-comparability, never a Match.
                non_comparable=True
                continue
            same=a["start"]==b["start"] and a["end"]==b["end"]
            overlap=a["start"]<b["end"] and b["start"]<a["end"]
            if same:relations.append({"relation":"DUPLICATE","subjects":[a["assertion_id"],b["assertion_id"]],"carrier":"match_relation","coordinate_space":proof})
            elif overlap:relations.append({"relation":"OVERLAP","subjects":[a["assertion_id"],b["assertion_id"]],"carrier":"match_relation","coordinate_space":proof})
    if relations:determination="RELATIONS_RECORDED"
    elif non_comparable:determination=NON_COMPARABILITY_TOKEN
    else:determination="NONE_DETECTED"
    return {"candidates":records,"relations":relations,"determination":determination}
