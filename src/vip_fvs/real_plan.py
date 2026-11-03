"""Narrow, local REAL-plan bridge for the real-source FVS.

This module deliberately does not render, export, probe media, or alter the
Gate-3 mapping vocabulary.  It converts a sealed review bundle plus an exact
ACCEPT decision into one typed placement and one direct source-PTS mapping.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

from gate3.editorial import EditorialDecision
from gate3.plan import EditPlanRevision
from gate3.placement import TimelinePlacement
from gate3.rational import TimeBase
from gate3.timeline import TimelineDomain
import gate3.refinement as _gate3_refinement
import gate3.authority as _gate3_authority

from .human_decision import HumanDecisionArtifact
from .review_bundle import ReviewBundle

_SCHEMA_VERSION = "vip_fvs.real_plan.v1"
_SCHEMA_VERSION_MULTI = "vip_fvs.real_plan.v2"
_SCHEMA_VERSION_LINEAGE = "vip_fvs.real_plan.v3"
_RECORD_FIELDS = {"schema_version", "plan", "placement", "mapping", "projected_decision",
                  "plan_digest", "placement_digest", "mapping_digest", "record_digest"}
_MULTI_RECORD_FIELDS = {"schema_version", "plan", "placements", "mappings", "projected_decisions",
                        "plan_digest", "placement_digests", "mapping_digests", "record_digest"}
_LINEAGE_RECORD_FIELDS = _MULTI_RECORD_FIELDS | {"lineage"}
_LINEAGE_FIELDS = {"placement_id", "order_index", "refinement_id", "decision_id",
                   "review_bundle_record_digest", "review_bundle_dependency_digest",
                   "human_decision_record_digest"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _int(value: Any, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")


@dataclass(frozen=True)
class SourceTimelineMapping:
    mapping_id: str
    source_refinement_id: str
    source_timebase_num: int
    source_timebase_den: int
    source_start_pts: int
    source_end_pts: int
    timeline_domain: TimelineDomain
    offset_ticks: int
    scale_num: int
    scale_den: int
    record_digest: str = field(default="")

    def __post_init__(self) -> None:
        for name in ("mapping_id", "source_refinement_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")
        for name in ("source_timebase_num", "source_timebase_den", "source_start_pts", "source_end_pts",
                     "offset_ticks", "scale_num", "scale_den"):
            _int(getattr(self, name), name)
        if self.source_timebase_num <= 0 or self.source_timebase_den <= 0:
            raise ValueError("source timebase must be positive")
        if self.source_end_pts <= self.source_start_pts:
            raise ValueError("source interval must be non-empty half-open")
        if not isinstance(self.timeline_domain, TimelineDomain):
            raise TypeError("timeline_domain must be a TimelineDomain")
        if (self.timeline_domain.time_base.num, self.timeline_domain.time_base.den) != (
                self.source_timebase_num, self.source_timebase_den):
            raise ValueError("source and timeline timebases must match exactly")
        if self.offset_ticks != -self.source_start_pts or self.scale_num != 1 or self.scale_den != 1:
            raise ValueError("only direct 1/1 source-PTS mapping is admitted")
        expected = self.compute_digest()
        if self.record_digest and self.record_digest != expected:
            raise ValueError("mapping digest mismatch")
        object.__setattr__(self, "record_digest", expected)

    def _preimage(self) -> dict[str, Any]:
        return {"mapping_id": self.mapping_id, "source_refinement_id": self.source_refinement_id,
                "source_timebase_num": self.source_timebase_num, "source_timebase_den": self.source_timebase_den,
                "source_start_pts": self.source_start_pts, "source_end_pts": self.source_end_pts,
                "timeline_domain": {"domain_id": self.timeline_domain.domain_id,
                                    "domain_name": self.timeline_domain.domain_name,
                                    "time_base": {"num": self.timeline_domain.time_base.num,
                                                   "den": self.timeline_domain.time_base.den}},
                "offset_ticks": self.offset_ticks, "scale_num": self.scale_num, "scale_den": self.scale_den}

    def compute_digest(self) -> str:
        return _digest(self._preimage())

    def to_record(self) -> dict[str, Any]:
        return {**self._preimage(), "record_digest": self.record_digest}

    def timeline_tick(self, source_pts: int) -> int:
        _int(source_pts, "source_pts")
        if not self.source_start_pts <= source_pts < self.source_end_pts:
            raise ValueError("source_pts outside half-open mapping interval")
        return source_pts + self.offset_ticks


@dataclass(frozen=True)
class RealPlanArtifacts:
    plan: EditPlanRevision
    placement: TimelinePlacement
    mapping: SourceTimelineMapping
    projected_decision: EditorialDecision
    plan_digest: str
    placement_digest: str
    mapping_digest: str
    placements: tuple[TimelinePlacement, ...] = ()
    mappings: tuple[SourceTimelineMapping, ...] = ()
    projected_decisions: tuple[EditorialDecision, ...] = ()
    lineage: tuple["RealPlanLineage", ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.lineage, tuple):
            raise TypeError("lineage must be an immutable tuple")
        if any(not isinstance(item, RealPlanLineage) for item in self.lineage):
            raise TypeError("lineage must contain RealPlanLineage records")


@dataclass(frozen=True)
class RealPlanLineage:
    placement_id: str
    order_index: int
    refinement_id: str
    decision_id: str
    review_bundle_record_digest: str
    review_bundle_dependency_digest: str
    human_decision_record_digest: str

    def __post_init__(self) -> None:
        for name in ("placement_id", "refinement_id", "decision_id"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")
        _int(self.order_index, "order_index")
        if self.order_index < 0:
            raise ValueError("order_index must be non-negative")
        for name in ("review_bundle_record_digest", "review_bundle_dependency_digest",
                     "human_decision_record_digest"):
            if not isinstance(getattr(self, name), str) or re.fullmatch(r"[0-9a-f]{64}", getattr(self, name)) is None:
                raise ValueError(f"{name} must be a lowercase SHA-256 digest")

    def to_record(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in (
            "placement_id", "order_index", "refinement_id", "decision_id",
            "review_bundle_record_digest", "review_bundle_dependency_digest",
            "human_decision_record_digest")}


@dataclass(frozen=True)
class RealPlanSelection:
    """One independently reviewed, measured source selection for a REAL plan."""
    bundle: ReviewBundle
    decision: HumanDecisionArtifact
    track: str = "V1"
    timeline_start_ticks: int = 0
    order_index: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.bundle, ReviewBundle) or not isinstance(self.decision, HumanDecisionArtifact):
            raise TypeError("selection requires a ReviewBundle and HumanDecisionArtifact")
        if not isinstance(self.track, str) or not self.track.strip():
            raise ValueError("track must be non-empty")
        _int(self.timeline_start_ticks, "timeline_start_ticks")
        if self.order_index is not None:
            _int(self.order_index, "order_index")
        if self.timeline_start_ticks < 0 or (self.order_index is not None and self.order_index < 0):
            raise ValueError("timeline start and order index must be non-negative")


def _validate_pins(bundle: ReviewBundle, decision: HumanDecisionArtifact) -> dict[str, Any]:
    if not isinstance(bundle, ReviewBundle) or not isinstance(decision, HumanDecisionArtifact):
        raise TypeError("bundle and decision types are required")
    bp = bundle.payload; dp = decision.payload
    if bp["review_status"] != "AWAITING_EDITORIAL_DECISION" or bp["decision"] is not None:
        raise ValueError("bundle is not an undecided sealed review bundle")
    if dp["decision_class"] != "ACCEPT" or dp["disposition"] != "ACCEPTED_FOR_PLAN" or dp["plan_action"] != "BUILD_REAL_PLAN":
        raise ValueError("only ACCEPT decisions can construct a REAL plan")
    checks = (("bundle_record_digest", bundle.record_digest), ("bundle_dependency_digest", bundle.dependency_digest),
              ("refinement_id", bp["refinement"]["refinement_id"]),
              ("refinement_evidence_digest", bp["refinement"]["evidence_digest"]),
              ("source_revision_id", bp["source"]["source_revision_id"]),
              ("source_sha256", bp["source"]["source_sha256"]))
    for field, expected in checks:
        if dp[field] != expected:
            raise ValueError(f"decision {field} pin mismatch")
    accepted = dp.get("accepted_sub_interval_ref")
    if accepted is not None and accepted != bp["refinement"]["refinement_id"]:
        raise ValueError("accepted_sub_interval_ref must equal the reviewed refinement_id")
    return bp


def _validate_selection_order(selections: list[RealPlanSelection] | tuple[RealPlanSelection, ...]) -> None:
    for index, selection in enumerate(selections):
        if not isinstance(selection, RealPlanSelection):
            raise TypeError("selections must contain only RealPlanSelection")
        if selection.order_index is not None and selection.order_index != index:
            raise ValueError("selection order_index must equal its sequence position")


def to_gate3_editorial_decision(decision: HumanDecisionArtifact) -> EditorialDecision:
    if not isinstance(decision, HumanDecisionArtifact) or decision.payload["decision_class"] != "ACCEPT":
        raise ValueError("only ACCEPT may be projected")
    p = decision.payload
    return EditorialDecision(decision_id=p["decision_id"], principal_kind="human", principal_ref=p["principal_ref"],
                             decided_on_refinement=p["refinement_id"], decided_on_revision=p["target_plan_revision"],
                             decision_class="ACCEPT", rationale=p["rationale"],
                             accepted_sub_interval_ref=p["accepted_sub_interval_ref"])


def _construct_real_plan(*, plan_id: str, plan_revision: int, placement: TimelinePlacement,
                         refinement_id: str, refinement: Mapping[str, Any],
                         projected: EditorialDecision, source_revision_ids: list[str],
                         evidence_digest: str,
                         supersedes: str | None = None,
                         derived_from_refs: list[str] | None = None,
                         prior_revision: Any | None = None,
                         plan_scope: str = "REAL") -> EditPlanRevision:
    """Construct a REAL or fixture plan through Gate-3's own constructor.

    ``plan_scope`` defaults to ``REAL`` so every historical REAL call site stays
    byte-identical; the fixture bridge is the only caller that passes
    ``SYNTHETIC_FIXTURE``.
    """
    if plan_scope not in ("REAL", "SYNTHETIC_FIXTURE"):
        raise ValueError("invalid plan_scope")
    return EditPlanRevision(
        plan_id, plan_revision, [placement], {refinement_id: refinement},
        {refinement_id: projected}, source_revision_ids, plan_scope=plan_scope,
        supersedes=supersedes, derived_from_refs=list(derived_from_refs or ()),
        prior_revision=prior_revision,
        pinned_evidence_digests={refinement_id: evidence_digest},
    )


def _load_authoritative_refinement(summary: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve the full byte-bound refinement pinned by a ReviewBundle summary."""
    ref_path = Path(str(summary.get("evidence_artifact_ref", "")))
    try:
        raw = ref_path.read_bytes()
        record = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        raise ValueError("authoritative refinement artifact unavailable") from exc
    if not isinstance(record, dict):
        raise ValueError("authoritative refinement evidence digest mismatch")
    recomputed = _gate3_authority.assert_evidence_digest(_gate3_authority.RECORD_KIND_REFINEMENT, record)
    if not isinstance(recomputed, str) or recomputed != record.get("evidence_digest") or recomputed != summary.get("evidence_digest"):
        raise ValueError("authoritative refinement evidence digest mismatch")
    if (record.get("source_probe_artifact_ref") != source.get("probe_artifact_ref") or
            record.get("source_probe_digest") != source.get("probe_digest")):
        raise ValueError("authoritative refinement source probe authority mismatch")
    if _gate3_refinement.is_binding_eligible(record) is not True:
        raise ValueError("authoritative refinement is not binding eligible")
    interval = summary["source_pts_interval"]
    if any((record.get(k) != v) for k, v in {
        "refinement_id": summary["refinement_id"],
        "source_revision_id": summary["source_revision_id"],
        "stream_index": summary["selected_stream_index"],
        "start_ticks": interval["start"], "end_ticks": interval["end"],
        "source_content_digest": None,
    }.items() if k != "source_content_digest"):
        raise ValueError("authoritative refinement summary mismatch")
    if record.get("time_base") != summary.get("timebase"):
        raise ValueError("authoritative refinement timebase mismatch")
    return record


def build_real_edit_plan(bundle: ReviewBundle, decision: HumanDecisionArtifact, *, plan_id: str,
                         plan_revision: int, pinned_evidence_digests: Mapping[str, str] | None = None,
                         policy_decision_ref: str | None = None,
                         prior_revision: EditPlanRevision | None = None) -> RealPlanArtifacts:
    bp = _validate_pins(bundle, decision)
    if not isinstance(plan_id, str) or not plan_id.strip() or isinstance(plan_revision, bool) or not isinstance(plan_revision, int) or plan_revision < 1:
        raise ValueError("plan identity is invalid")
    if policy_decision_ref is not None:
        raise ValueError("Task 5 cannot fabricate policy authority")
    if prior_revision is not None and not isinstance(prior_revision, EditPlanRevision):
        raise ValueError("PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION")
    if plan_revision == 1:
        if prior_revision is not None:
            raise ValueError("PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION")
    elif prior_revision is None:
        raise ValueError("PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION")
    else:
        if prior_revision.plan_revision != plan_revision - 1:
            raise ValueError("PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION")
        if prior_revision.plan_id != plan_id:
            raise ValueError("PRIOR_REVISION_MUST_SHARE_PLAN_ID")
        if prior_revision.plan_scope != "REAL":
            raise ValueError("PRIOR_REVISION_MUST_HAVE_COMPATIBLE_PLAN_SCOPE")
    summary = bp["refinement"]
    full_ref = _load_authoritative_refinement(summary, bp["source"])
    if full_ref.get("source_content_digest") != bp["source"]["source_sha256"]:
        raise ValueError("authoritative refinement source digest mismatch")
    rid = summary["refinement_id"]
    if pinned_evidence_digests is not None and dict(pinned_evidence_digests) != {rid: summary["evidence_digest"]}:
        raise ValueError("evidence pin mismatch")
    # Re-measure through Gate-3's binding predicate.  The tests use a synthetic
    # measured seam; no source bytes or provider are accessed here.
    ref = {
        **full_ref,
        "source_pts_interval": dict(summary["source_pts_interval"]),
        "timebase": dict(summary["timebase"]),
        "selected_stream_index": summary["selected_stream_index"],
        "evidence_artifact_ref": summary["evidence_artifact_ref"],
        "evidence_digest": summary["evidence_digest"],
    }
    interval = ref["source_pts_interval"]
    if interval["time_domain"] != "source_pts" or interval["endpoint_semantics"] != "half_open":
        raise ValueError("source authority must be integer source PTS")
    start, end = interval["start"], interval["end"]
    _int(start, "source start"); _int(end, "source end")
    if end <= start or ref["timebase"] != bp["source"]["timebase"]:
        raise ValueError("invalid measured source interval")
    mapping = SourceTimelineMapping("mapping-" + plan_id, rid, ref["timebase"]["num"], ref["timebase"]["den"], start, end,
                                    TimelineDomain(plan_id + "-timeline", TimeBase(ref["timebase"]["num"], ref["timebase"]["den"])),
                                    -start, 1, 1)
    projected = to_gate3_editorial_decision(decision)
    # D-REALPLAN-1: the newly supplied decision must target this exact revision.
    # Gate-3's own bound is `1 <= decided_on_revision <= plan_revision` and stays
    # untouched because it is correct for decisions INHERITED through prior-plan
    # lineage; it cannot substitute for this exact predicate, and an older-target
    # decision must never be newly supplied as the authority for a higher revision.
    if projected.decided_on_revision != plan_revision:
        raise ValueError("PLAN_REVISION_MUST_MATCH_DECISION_REVISION")
    placement = TimelinePlacement("placement-" + plan_id, plan_id, plan_revision, rid, projected.decision_id,
                                  "V1", 0, 0, end - start, mapping.mapping_id, mapping.timeline_domain)
    placement_digest = _digest(placement.to_record())
    if prior_revision is None:
        plan = _construct_real_plan(
            plan_id=plan_id, plan_revision=plan_revision, placement=placement,
            refinement_id=rid, refinement=ref, projected=projected,
            source_revision_ids=[ref["source_revision_id"]],
            evidence_digest=ref["evidence_digest"],
        )
    else:
        # An explicit prior revision advances through Gate-3's own constructor so
        # that supersedes/derived_from_refs/prior_revision and the plan_id and
        # revision continuity are enforced by Gate-3 rather than re-implemented.
        from gate3.plan import new_revision

        plan = new_revision(
            prior_revision,
            placements=[placement],
            pinned_refinements={rid: ref},
            pinned_decisions={rid: projected},
            source_revision_ids=[ref["source_revision_id"]],
            pinned_evidence_digests={rid: ref["evidence_digest"]},
        )
    return RealPlanArtifacts(plan, placement, mapping, projected, plan.digest, placement_digest, mapping.record_digest)


def build_fixture_plan_artifacts(*, plan_id: str, plan_revision: int,
                                 decision: EditorialDecision,
                                 refinement: Mapping[str, Any],
                                 prior_revision: EditPlanRevision | None = None) -> RealPlanArtifacts:
    """Build a SYNTHETIC_FIXTURE plan from generated-media measured evidence only.

    This is the fixture-only sibling of :func:`build_real_edit_plan`.  It never
    reads a ``ReviewBundle``/``HumanDecisionArtifact`` and never claims human
    editorial authority: the decision must be a ``SYNTHETIC_HUMAN`` decision
    carrying ``fixture_scope="SYNTHETIC_FIXTURE"``, and the refinement must be a
    MEASURED, binding-eligible, evidence-digest-pinned record.
    """
    if (not isinstance(plan_id, str) or not plan_id.strip()
            or isinstance(plan_revision, bool) or not isinstance(plan_revision, int)
            or plan_revision < 1):
        raise ValueError("FIXTURE_PLAN_IDENTITY_INVALID")
    if plan_revision == 1:
        if prior_revision is not None:
            raise ValueError("FIXTURE_PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION")
    elif prior_revision is None:
        raise ValueError("FIXTURE_PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION")
    else:
        if not isinstance(prior_revision, EditPlanRevision):
            raise ValueError("FIXTURE_PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION")
        if prior_revision.plan_revision != plan_revision - 1:
            raise ValueError("FIXTURE_PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION")
        if prior_revision.plan_id != plan_id:
            raise ValueError("FIXTURE_PRIOR_REVISION_MUST_SHARE_PLAN_ID")
        if prior_revision.plan_scope != "SYNTHETIC_FIXTURE":
            raise ValueError("FIXTURE_PRIOR_REVISION_SCOPE_MISMATCH")
    if not isinstance(decision, EditorialDecision):
        raise ValueError("FIXTURE_DECISION_REQUIRED: an EditorialDecision is required")
    if decision.principal_kind != "SYNTHETIC_HUMAN" or decision.fixture_scope != "SYNTHETIC_FIXTURE":
        raise ValueError("FIXTURE_DECISION_REQUIRED: a SYNTHETIC_HUMAN decision scoped SYNTHETIC_FIXTURE is required")
    if decision.decision_class != "ACCEPT":
        raise ValueError("FIXTURE_DECISION_CLASS_INVALID")
    if not isinstance(refinement, Mapping):
        raise ValueError("FIXTURE_REFINEMENT_REQUIRED")
    rid = refinement.get("refinement_id")
    if not isinstance(rid, str) or not rid:
        raise ValueError("FIXTURE_REFINEMENT_REQUIRED")
    if decision.decided_on_refinement != rid:
        raise ValueError("FIXTURE_DECISION_REFINEMENT_MISMATCH")
    if decision.decided_on_revision != plan_revision:
        raise ValueError("FIXTURE_DECISION_REVISION_MISMATCH")
    full = dict(refinement)
    if full.get("evidence_class") != "MEASURED":
        raise ValueError("FIXTURE_REFINEMENT_NOT_MEASURED")
    if _gate3_refinement.is_binding_eligible(full) is not True:
        raise ValueError("FIXTURE_REFINEMENT_NOT_BINDING")
    interval = full.get("source_pts_interval")
    start = interval.get("start") if isinstance(interval, Mapping) else None
    end = interval.get("end") if isinstance(interval, Mapping) else None
    if (not isinstance(interval, Mapping) or interval.get("time_domain") != "source_pts"
            or interval.get("endpoint_semantics") != "half_open"
            or isinstance(start, bool) or not isinstance(start, int)
            or isinstance(end, bool) or not isinstance(end, int) or end <= start):
        raise ValueError("FIXTURE_REFINEMENT_INTERVAL_INVALID")
    timebase = full.get("timebase")
    if not isinstance(timebase, Mapping) or set(timebase) != {"num", "den"}:
        raise ValueError("FIXTURE_REFINEMENT_TIMEBASE_INVALID")
    for name in ("num", "den"):
        value = timebase[name]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("FIXTURE_REFINEMENT_TIMEBASE_INVALID")
    declared_base = full.get("time_base")
    if declared_base is not None and dict(declared_base) != dict(timebase):
        raise ValueError("FIXTURE_REFINEMENT_TIMEBASE_INVALID")
    for name, expected in (("start_ticks", start), ("end_ticks", end)):
        if name in full and full[name] != expected:
            raise ValueError("FIXTURE_REFINEMENT_INTERVAL_INVALID")
    evidence_digest = full.get("evidence_digest")
    if (not isinstance(evidence_digest, str) or len(evidence_digest) != 64
            or any(c not in "0123456789abcdef" for c in evidence_digest)):
        raise ValueError("FIXTURE_REFINEMENT_EVIDENCE_REQUIRED")
    source_revision_id = full.get("source_revision_id")
    source_revision_ids = [source_revision_id] if isinstance(source_revision_id, str) and source_revision_id else []
    mapping = SourceTimelineMapping(
        "mapping-" + plan_id, rid, timebase["num"], timebase["den"], start, end,
        TimelineDomain(plan_id + "-timeline", TimeBase(timebase["num"], timebase["den"])),
        -start, 1, 1,
    )
    placement = TimelinePlacement("placement-" + plan_id, plan_id, plan_revision, rid, decision.decision_id,
                                  "V1", 0, 0, end - start, mapping.mapping_id, mapping.timeline_domain)
    placement_digest = _digest(placement.to_record())
    if prior_revision is None:
        plan = _construct_real_plan(
            plan_id=plan_id, plan_revision=plan_revision, placement=placement,
            refinement_id=rid, refinement=full, projected=decision,
            source_revision_ids=source_revision_ids,
            evidence_digest=evidence_digest,
            plan_scope="SYNTHETIC_FIXTURE",
        )
    else:
        from gate3.plan import new_revision

        plan = new_revision(
            prior_revision,
            placements=[placement],
            pinned_refinements={rid: full},
            pinned_decisions={rid: decision},
            source_revision_ids=source_revision_ids or list(prior_revision.source_revision_ids),
            pinned_evidence_digests={rid: evidence_digest},
        )
    return RealPlanArtifacts(plan, placement, mapping, decision, plan.digest,
                             placement_digest, mapping.record_digest)


def build_real_edit_plan_from_selections(selections: list[RealPlanSelection] | tuple[RealPlanSelection, ...], *,
                                         plan_id: str, plan_revision: int,
                                         prior_revision: EditPlanRevision | None = None) -> RealPlanArtifacts:
    """Assemble a deterministic multi-selection REAL plan from fresh per-selection authority.

    Every selection contributes its own current ACCEPT decision and measured evidence pins.
    A successor deliberately receives only the newly supplied selections; Gate-3 history is
    linked by digest, while old decisions are not copied as authority for changed selections.
    """
    if not isinstance(selections, (list, tuple)) or not selections:
        raise ValueError("at least one RealPlanSelection is required")
    if not isinstance(plan_id, str) or not plan_id.strip() or isinstance(plan_revision, bool) or not isinstance(plan_revision, int) or plan_revision < 1:
        raise ValueError("plan identity is invalid")
    if plan_revision == 1 and prior_revision is not None:
        raise ValueError("PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION")
    if plan_revision > 1:
        if not isinstance(prior_revision, EditPlanRevision):
            raise ValueError("PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION")
        if prior_revision is None:
            raise ValueError("PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION")
        if prior_revision.plan_revision != plan_revision - 1:
            raise ValueError("PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION")
        if prior_revision.plan_id != plan_id:
            raise ValueError("PRIOR_REVISION_MUST_SHARE_PLAN_ID")
        if prior_revision.plan_scope != "REAL":
            raise ValueError("PRIOR_REVISION_MUST_HAVE_COMPATIBLE_PLAN_SCOPE")

    placements: list[TimelinePlacement] = []
    mappings: list[SourceTimelineMapping] = []
    projected_decisions: list[EditorialDecision] = []
    refinements: dict[str, dict[str, Any]] = {}
    decisions: dict[str, EditorialDecision] = {}
    evidence_digests: dict[str, str] = {}
    source_revision_ids: list[str] = []
    common_timebase: tuple[int, int] | None = None
    _validate_selection_order(selections)
    for index, selection in enumerate(selections):
        if not isinstance(selection, RealPlanSelection):
            raise TypeError("selections must contain only RealPlanSelection")
        bp = _validate_pins(selection.bundle, selection.decision)
        summary = bp["refinement"]
        full_ref = _load_authoritative_refinement(summary, bp["source"])
        if full_ref.get("source_content_digest") != bp["source"]["source_sha256"]:
            raise ValueError("authoritative refinement source digest mismatch")
        rid = summary["refinement_id"]
        if rid in refinements:
            raise ValueError("selection refinement ids must be unique")
        projected = to_gate3_editorial_decision(selection.decision)
        if projected.decided_on_revision != plan_revision:
            raise ValueError("PLAN_REVISION_MUST_MATCH_DECISION_REVISION")
        ref = {**full_ref, "source_pts_interval": dict(summary["source_pts_interval"]),
               "timebase": dict(summary["timebase"]), "selected_stream_index": summary["selected_stream_index"],
               "evidence_artifact_ref": summary["evidence_artifact_ref"], "evidence_digest": summary["evidence_digest"]}
        interval = ref["source_pts_interval"]
        if interval["time_domain"] != "source_pts" or interval["endpoint_semantics"] != "half_open":
            raise ValueError("source authority must be integer source PTS")
        start, end = interval["start"], interval["end"]
        _int(start, "source start"); _int(end, "source end")
        if end <= start or ref["timebase"] != bp["source"]["timebase"]:
            raise ValueError("invalid measured source interval")
        tb = ref["timebase"]
        identity = (tb["num"], tb["den"])
        if common_timebase is None:
            common_timebase = identity
        elif common_timebase != identity:
            raise ValueError("multi-selection timeline domains require one exact timebase")
        mapping_id = f"mapping-{plan_id}-{index}"
        domain = TimelineDomain(plan_id + "-timeline", TimeBase(*identity))
        mapping = SourceTimelineMapping(mapping_id, rid, tb["num"], tb["den"], start, end,
                                        domain, -start, 1, 1)
        placement = TimelinePlacement(
            f"placement-{plan_id}-{index}", plan_id, plan_revision, rid, projected.decision_id,
            selection.track, index if selection.order_index is None else selection.order_index, selection.timeline_start_ticks,
            selection.timeline_start_ticks + (end - start), mapping_id, domain)
        placements.append(placement); mappings.append(mapping); projected_decisions.append(projected)
        refinements[rid] = ref; decisions[rid] = projected
        evidence_digests[rid] = ref["evidence_digest"]
        if ref["source_revision_id"] not in source_revision_ids:
            source_revision_ids.append(ref["source_revision_id"])

    if prior_revision is None:
        plan = EditPlanRevision(plan_id, plan_revision, placements, refinements, decisions,
                                source_revision_ids, plan_scope="REAL",
                                pinned_evidence_digests=evidence_digests)
    else:
        from gate3.plan import new_revision
        plan = new_revision(prior_revision, placements=placements, pinned_refinements=refinements,
                            pinned_decisions=decisions, source_revision_ids=source_revision_ids,
                            pinned_evidence_digests=evidence_digests)
    placement_digests = tuple(_digest(p.to_record()) for p in placements)
    mapping_digests = tuple(m.record_digest for m in mappings)
    return RealPlanArtifacts(plan, placements[0], mappings[0], projected_decisions[0], plan.digest,
                             placement_digests[0], mapping_digests[0], tuple(placements), tuple(mappings),
                             tuple(projected_decisions))


def _lineage_for_selection(selection: RealPlanSelection, placement: TimelinePlacement, index: int) -> RealPlanLineage:
    bp = _validate_pins(selection.bundle, selection.decision)
    return RealPlanLineage(placement.placement_id, index, bp["refinement"]["refinement_id"],
        selection.decision.payload["decision_id"], selection.bundle.record_digest,
        selection.bundle.dependency_digest, selection.decision.record_digest)


def build_real_edit_plan_with_lineage(bundle: ReviewBundle, decision: HumanDecisionArtifact, *, plan_id: str,
                                      plan_revision: int, pinned_evidence_digests: Mapping[str, str] | None = None,
                                      policy_decision_ref: str | None = None,
                                      prior_revision: EditPlanRevision | None = None) -> RealPlanArtifacts:
    selection = RealPlanSelection(bundle, decision)
    bp = _validate_pins(bundle, decision)
    if pinned_evidence_digests is not None and dict(pinned_evidence_digests) != {
            bp["refinement"]["refinement_id"]: bp["refinement"]["evidence_digest"]}:
        raise ValueError("evidence pin mismatch")
    if policy_decision_ref is not None:
        raise ValueError("Task 5 cannot fabricate policy authority")
    return build_real_edit_plan_from_selections_with_lineage([selection], plan_id=plan_id,
        plan_revision=plan_revision, prior_revision=prior_revision)


def build_real_edit_plan_from_selections_with_lineage(
        selections: list[RealPlanSelection] | tuple[RealPlanSelection, ...], *, plan_id: str,
        plan_revision: int, prior_revision: EditPlanRevision | None = None) -> RealPlanArtifacts:
    built = build_real_edit_plan_from_selections(selections, plan_id=plan_id,
        plan_revision=plan_revision, prior_revision=prior_revision)
    lineage = tuple(_lineage_for_selection(item, placement, index)
                    for index, (item, placement) in enumerate(zip(selections, built.placements)))
    result = RealPlanArtifacts(built.plan, built.placement, built.mapping, built.projected_decision,
        built.plan_digest, built.placement_digest, built.mapping_digest, built.placements,
        built.mappings, built.projected_decisions, lineage)
    _validate_lineage_artifacts(result)
    return result


def _validate_lineage_artifacts(artifacts: RealPlanArtifacts) -> None:
    n = len(artifacts.placements)
    if not n or len(artifacts.mappings) != n or len(artifacts.projected_decisions) != n or len(artifacts.lineage) != n:
        raise ValueError("v3 lineage cardinality mismatch")
    if artifacts.plan.digest != artifacts.plan_digest:
        raise ValueError("plan digest mismatch")
    if (tuple(artifacts.plan.placements) != tuple(artifacts.placements) or
            artifacts.placement_digest != _digest(artifacts.placements[0].to_record()) or
            artifacts.mapping_digest != artifacts.mappings[0].record_digest):
        raise ValueError("v3 primary digest or plan link mismatch")
    pids: set[str] = set(); rids: set[str] = set(); dids: set[str] = set()
    for i, (lineage, placement, mapping, decision) in enumerate(zip(
            artifacts.lineage, artifacts.placements, artifacts.mappings, artifacts.projected_decisions)):
        if not isinstance(lineage, RealPlanLineage) or lineage.order_index != i or placement.order_index != i:
            raise ValueError("v3 lineage order mismatch")
        pinned_decision = artifacts.plan.pinned_decisions.get(lineage.refinement_id)
        if (lineage.placement_id != placement.placement_id or lineage.refinement_id != placement.source_interval_ref or
                lineage.refinement_id != mapping.source_refinement_id or lineage.decision_id != decision.decision_id or
                lineage.decision_id != placement.editorial_decision_ref or mapping.mapping_id != placement.mapping_artifact_ref or
                placement.plan_id != artifacts.plan.plan_id or placement.plan_revision != artifacts.plan.plan_revision or
                decision.decided_on_refinement != lineage.refinement_id or decision.decided_on_revision != artifacts.plan.plan_revision or
                pinned_decision is None or pinned_decision.decision_id != lineage.decision_id):
            raise ValueError("v3 lineage cross-link mismatch")
        if artifacts.plan.pinned_decisions.get(lineage.refinement_id) != decision:
            raise ValueError("v3 projected decision link mismatch")
        if lineage.placement_id in pids or lineage.refinement_id in rids or lineage.decision_id in dids:
            raise ValueError("v3 lineage identities must be unique")
        pids.add(lineage.placement_id); rids.add(lineage.refinement_id); dids.add(lineage.decision_id)
    if (artifacts.placement != artifacts.placements[0] or artifacts.mapping != artifacts.mappings[0] or
            artifacts.projected_decision != artifacts.projected_decisions[0]):
        raise ValueError("v3 primary selection mismatch")


def rebind_real_plan_selections(artifacts: RealPlanArtifacts,
                                selections: list[RealPlanSelection] | tuple[RealPlanSelection, ...]
                                ) -> tuple[RealPlanSelection, ...]:
    if not isinstance(artifacts, RealPlanArtifacts) or not artifacts.lineage:
        raise ValueError("rebind requires a verified v3 real plan")
    if not isinstance(selections, (list, tuple)):
        raise ValueError("selections must be an ordered list or tuple")
    try:
        _validate_selection_order(selections)
    except TypeError as exc:
        raise ValueError("rebind selections are invalid") from exc
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    _validate_lineage_artifacts(artifacts)
    if len(selections) != len(artifacts.lineage):
        raise ValueError("rebind selection cardinality mismatch")
    expected: list[RealPlanLineage] = []
    for index, (selection, placement) in enumerate(zip(selections, artifacts.placements)):
        expected.append(_lineage_for_selection(selection, placement, index))
    if tuple(expected) != artifacts.lineage:
        raise ValueError("rebind source lineage mismatch")
    return tuple(selections)


def save_real_plan(artifacts: RealPlanArtifacts, path: str | os.PathLike[str]) -> Path:
    if not isinstance(artifacts, RealPlanArtifacts): raise TypeError("artifacts required")
    if artifacts.lineage:
        _validate_lineage_artifacts(artifacts)
        placements = artifacts.placements
        mappings = artifacts.mappings
        decisions = artifacts.projected_decisions
        placement_digests = [_digest(p.to_record()) for p in placements]
        record = {"schema_version": _SCHEMA_VERSION_LINEAGE, "plan": artifacts.plan.to_record(),
                  "placements": [p.to_record() for p in placements],
                  "mappings": [m.to_record() for m in mappings],
                  "projected_decisions": [d.to_record() for d in decisions],
                  "plan_digest": artifacts.plan_digest, "placement_digests": placement_digests,
                  "mapping_digests": [m.record_digest for m in mappings],
                  "lineage": [lineage.to_record() for lineage in artifacts.lineage]}
    elif artifacts.placements:
        placements = artifacts.placements
        mappings = artifacts.mappings
        decisions = artifacts.projected_decisions
        placement_digests = [_digest(p.to_record()) for p in placements]
        record = {"schema_version": _SCHEMA_VERSION_MULTI, "plan": artifacts.plan.to_record(),
                  "placements": [p.to_record() for p in placements],
                  "mappings": [m.to_record() for m in mappings],
                  "projected_decisions": [d.to_record() for d in decisions],
                  "plan_digest": artifacts.plan_digest, "placement_digests": placement_digests,
                  "mapping_digests": [m.record_digest for m in mappings]}
    else:
        record = {"schema_version": _SCHEMA_VERSION, "plan": artifacts.plan.to_record(),
              "placement": artifacts.placement.to_record(), "mapping": artifacts.mapping.to_record(),
              "projected_decision": artifacts.projected_decision.to_record(), "plan_digest": artifacts.plan_digest,
              "placement_digest": artifacts.placement_digest, "mapping_digest": artifacts.mapping_digest}
    record["record_digest"] = _digest(record)
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = load_real_plan(target)
        if (existing.plan_digest == artifacts.plan_digest and existing.placement_digest == artifacts.placement_digest and
                existing.mapping_digest == artifacts.mapping_digest and existing.lineage == artifacts.lineage):
            return target
        raise ValueError("sealed real plan differs")
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"); fh.flush(); os.fsync(fh.fileno())
    try:
        os.link(tmp, target)
    except FileExistsError:
        existing = load_real_plan(target)
        if (existing.plan_digest == artifacts.plan_digest and existing.placement_digest == artifacts.placement_digest and
                existing.mapping_digest == artifacts.mapping_digest and existing.lineage == artifacts.lineage):
            return target
        raise ValueError("sealed real plan differs")
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
    directory_fd = os.open(target.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return target


def _load_multi_record(record: Mapping[str, Any]) -> RealPlanArtifacts:
    plan_record = record["plan"]
    raw_revision = plan_record.get("plan_revision")
    supersedes = plan_record.get("supersedes")
    derived = plan_record.get("derived_from_refs", [])
    if (isinstance(raw_revision, bool) or not isinstance(raw_revision, int) or
            not isinstance(derived, list) or
            (raw_revision == 1 and (supersedes is not None or derived)) or
            (raw_revision > 1 and (not isinstance(supersedes, str) or derived != [supersedes])) or
            raw_revision < 1):
        raise ValueError("REAL_PLAN_LINEAGE_READBACK_MISMATCH")
    raw_placements = record["placements"]
    raw_mappings = record["mappings"]
    raw_decisions = record["projected_decisions"]
    if (not isinstance(raw_placements, list) or not raw_placements or
            not isinstance(raw_mappings, list) or len(raw_mappings) != len(raw_placements) or
            not isinstance(raw_decisions, list) or len(raw_decisions) != len(raw_placements) or
            len(record["placement_digests"]) != len(raw_placements) or
            len(record["mapping_digests"]) != len(raw_mappings)):
        raise ValueError("multi-selection real plan cardinality mismatch")
    mappings: list[SourceTimelineMapping] = []
    placements: list[TimelinePlacement] = []
    decisions: list[EditorialDecision] = []
    for m in raw_mappings:
        domain = m["timeline_domain"]; tb = domain["time_base"]
        mappings.append(SourceTimelineMapping(m["mapping_id"], m["source_refinement_id"],
            m["source_timebase_num"], m["source_timebase_den"], m["source_start_pts"],
            m["source_end_pts"], TimelineDomain(domain["domain_id"], TimeBase(tb["num"], tb["den"]), domain.get("domain_name", "timeline_time")),
            m["offset_ticks"], m["scale_num"], m["scale_den"], m["record_digest"]))
    for p in raw_placements:
        domain = p["timeline_domain"]; tb = domain["time_base"]
        placements.append(TimelinePlacement(p["placement_id"], p["plan_id"], p["plan_revision"],
            p["source_interval_ref"], p["editorial_decision_ref"], p["track"], p["order_index"],
            p["timeline_start_ticks"], p["timeline_end_ticks"], p["mapping_artifact_ref"],
            TimelineDomain(domain["domain_id"], TimeBase(tb["num"], tb["den"]), domain.get("domain_name", "timeline_time"))))
    for d in raw_decisions:
        decisions.append(EditorialDecision(d["decision_id"], d["principal_kind"], d["principal_ref"],
            d["decided_on_refinement"], d["decided_on_revision"], d["decision_class"], d["rationale"],
            d.get("options_considered", []), accepted_sub_interval_ref=d.get("accepted_sub_interval_ref"),
            presentation_manifest_ref=d.get("presentation_manifest_ref"),
            fixture_scope=d.get("fixture_scope")))
    refinements = plan_record["pinned_refinements"]
    pinned_decisions = plan_record["pinned_decisions"]
    if set(refinements) != set(pinned_decisions) or len(refinements) != len(placements):
        raise ValueError("multi-selection plan authority cardinality mismatch")
    by_rid = {m.source_refinement_id: (m, p, d) for m, p, d in zip(mappings, placements, decisions)}
    if set(by_rid) != set(refinements):
        raise ValueError("multi-selection refinement links mismatch")
    for rid, (mapping, placement, decision) in by_rid.items():
        interval = refinements[rid].get("source_pts_interval", {})
        timebase = refinements[rid].get("timebase", {})
        if (placement.mapping_artifact_ref != mapping.mapping_id or
                placement.source_interval_ref != rid or placement.editorial_decision_ref != decision.decision_id or
                decision.decision_id != pinned_decisions[rid]["decision_id"] or
                placement.timeline_domain != mapping.timeline_domain or
                placement.plan_id != plan_record["plan_id"] or placement.plan_revision != raw_revision or
                decision.decided_on_revision != raw_revision or
                mapping.source_start_pts != interval.get("start") or
                mapping.source_end_pts != interval.get("end") or
                (mapping.source_timebase_num, mapping.source_timebase_den) !=
                (timebase.get("num"), timebase.get("den"))):
            raise ValueError("multi-selection authority link mismatch")
    expected_sources = list(dict.fromkeys(ref.get("source_revision_id") for ref in refinements.values()))
    if plan_record.get("source_revision_ids") != expected_sources:
        raise ValueError("multi-selection source revision links mismatch")
    plan = EditPlanRevision(plan_record["plan_id"], raw_revision, placements, refinements,
        {d.decided_on_refinement: d for d in decisions}, plan_record["source_revision_ids"],
        supersedes=supersedes, derived_from_refs=derived, plan_scope=plan_record["plan_scope"],
        policy_decision_ref=plan_record.get("policy_decision_ref"),
        pinned_evidence_digests=plan_record["pinned_evidence_digests"])
    if plan.to_record() != dict(plan_record): raise ValueError("plan readback mismatch")
    if record["plan_digest"] != plan.digest: raise ValueError("plan digest mismatch")
    placement_digests = [_digest(p.to_record()) for p in placements]
    if record["placement_digests"] != placement_digests: raise ValueError("placement digest mismatch")
    mapping_digests = [m.record_digest for m in mappings]
    if record["mapping_digests"] != mapping_digests: raise ValueError("mapping digest mismatch")
    return RealPlanArtifacts(plan, placements[0], mappings[0], decisions[0], plan.digest,
        placement_digests[0], mapping_digests[0], tuple(placements), tuple(mappings), tuple(decisions))


def load_real_plan(path: str | os.PathLike[str]) -> RealPlanArtifacts:
    raw = Path(path).read_bytes()
    if not raw.endswith(b"\n"): raise ValueError("real plan is not sealed canonical JSON")
    try:
        record = json.loads(raw[:-1].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid real plan JSON") from exc
    if not isinstance(record, dict) or set(record) not in (_RECORD_FIELDS, _MULTI_RECORD_FIELDS, _LINEAGE_RECORD_FIELDS):
        raise ValueError("real plan envelope keys mismatch")
    if record.get("schema_version") not in (_SCHEMA_VERSION, _SCHEMA_VERSION_MULTI, _SCHEMA_VERSION_LINEAGE):
        raise ValueError("unexpected real plan schema version")
    expected_fields = {_SCHEMA_VERSION: _RECORD_FIELDS, _SCHEMA_VERSION_MULTI: _MULTI_RECORD_FIELDS,
                       _SCHEMA_VERSION_LINEAGE: _LINEAGE_RECORD_FIELDS}[record["schema_version"]]
    if set(record) != expected_fields:
        raise ValueError("real plan envelope keys mismatch")
    if not raw.endswith(b"\n") or _canonical(record) + b"\n" != raw:
        raise ValueError("real plan is not canonical sealed JSON")
    supplied = record.pop("record_digest", None)
    if supplied != _digest(record): raise ValueError("real plan record digest mismatch")
    if record.get("schema_version") == _SCHEMA_VERSION_LINEAGE:
        raw_lineage = record.get("lineage")
        if not isinstance(raw_lineage, list) or not raw_lineage:
            raise ValueError("v3 lineage cardinality mismatch")
        lineage = []
        for item in raw_lineage:
            if not isinstance(item, dict) or set(item) != _LINEAGE_FIELDS:
                raise ValueError("v3 lineage keys mismatch")
            lineage.append(RealPlanLineage(**item))
        multi_record = {key: value for key, value in record.items() if key != "lineage"}
        multi_record["schema_version"] = _SCHEMA_VERSION_MULTI
        try:
            loaded = _load_multi_record(multi_record)
            result = RealPlanArtifacts(loaded.plan, loaded.placement, loaded.mapping, loaded.projected_decision,
                loaded.plan_digest, loaded.placement_digest, loaded.mapping_digest, loaded.placements,
                loaded.mappings, loaded.projected_decisions, tuple(lineage))
            _validate_lineage_artifacts(result)
        except (KeyError, TypeError, AttributeError) as exc:
            raise ValueError("invalid v3 real plan record") from exc
        return result
    if record.get("schema_version") == _SCHEMA_VERSION_MULTI:
        return _load_multi_record(record)
    # D-REALPLAN-1 (raw lineage first): classify the sealed plan's raw lineage
    # BEFORE any Gate-3 object is constructed and before the plan-digest
    # comparison.  EditPlanRevision.__post_init__ rejects a malformed `supersedes`
    # with its own generic message, and SourceTimelineMapping/TimelinePlacement/
    # EditorialDecision can raise their own ValueError for unrelated malformed
    # fields, so classifying first is what guarantees the frozen Root-G refusal
    # code is not masked by a constructor-side error.  `plan.digest` is also
    # computed over `supersedes`, so this must precede that comparison.
    pr = record["plan"]
    raw_revision = pr.get("plan_revision")
    raw_supersedes = pr.get("supersedes")
    raw_derived_value = pr.get("derived_from_refs", [])
    if not isinstance(raw_derived_value, list):
        raise ValueError("REAL_PLAN_LINEAGE_READBACK_MISMATCH")
    raw_derived = list(raw_derived_value)
    if isinstance(raw_revision, bool) or not isinstance(raw_revision, int):
        raise ValueError("REAL_PLAN_LINEAGE_READBACK_MISMATCH")
    if raw_revision == 1:
        if raw_supersedes is not None or raw_derived:
            raise ValueError("REAL_PLAN_LINEAGE_READBACK_MISMATCH")
    elif raw_revision > 1:
        if (not isinstance(raw_supersedes, str)
                or re.fullmatch(r"[0-9a-f]+", raw_supersedes) is None
                or raw_derived != [raw_supersedes]):
            raise ValueError("REAL_PLAN_LINEAGE_READBACK_MISMATCH")
    else:
        raise ValueError("REAL_PLAN_LINEAGE_READBACK_MISMATCH")
    m = record["mapping"]; domain = m["timeline_domain"]; tb = domain["time_base"]
    mapping = SourceTimelineMapping(m["mapping_id"], m["source_refinement_id"], m["source_timebase_num"], m["source_timebase_den"], m["source_start_pts"], m["source_end_pts"], TimelineDomain(domain["domain_id"], TimeBase(tb["num"], tb["den"]), domain["domain_name"]), m["offset_ticks"], m["scale_num"], m["scale_den"], m["record_digest"])
    p = record["placement"]; ptb = p["timeline_domain"]["time_base"]
    placement = TimelinePlacement(p["placement_id"], p["plan_id"], p["plan_revision"], p["source_interval_ref"], p["editorial_decision_ref"], p["track"], p["order_index"], p["timeline_start_ticks"], p["timeline_end_ticks"], p["mapping_artifact_ref"], TimelineDomain(p["timeline_domain"]["domain_id"], TimeBase(ptb["num"], ptb["den"]), p["timeline_domain"].get("domain_name", "timeline_time")))
    d = record["projected_decision"]; projected = EditorialDecision(d["decision_id"], d["principal_kind"], d["principal_ref"], d["decided_on_refinement"], d["decided_on_revision"], d["decision_class"], d["rationale"], d.get("options_considered", []), accepted_sub_interval_ref=d.get("accepted_sub_interval_ref"), presentation_manifest_ref=d.get("presentation_manifest_ref"), fixture_scope=d.get("fixture_scope"))
    pr = record["plan"]; rid = next(iter(pr["pinned_refinements"]))
    readback_scope = pr.get("plan_scope", "REAL")
    if readback_scope not in ("REAL", "SYNTHETIC_FIXTURE"):
        raise ValueError("invalid plan_scope")
    plan = _construct_real_plan(
        plan_id=pr["plan_id"], plan_revision=pr["plan_revision"],
        placement=placement, refinement_id=rid,
        refinement=pr["pinned_refinements"][rid], projected=projected,
        source_revision_ids=pr["source_revision_ids"],
        evidence_digest=pr["pinned_evidence_digests"][rid],
        supersedes=raw_supersedes, derived_from_refs=raw_derived,
        plan_scope=readback_scope,
    )
    if plan.to_record() != record["plan"]: raise ValueError("plan readback mismatch")
    if record["plan_digest"] != plan.digest: raise ValueError("plan digest mismatch")
    expected_placement_digest = _digest(placement.to_record())
    if record["placement_digest"] != expected_placement_digest: raise ValueError("placement digest mismatch")
    if record["mapping_digest"] != mapping.record_digest: raise ValueError("mapping digest mismatch")
    if placement.mapping_artifact_ref != mapping.mapping_id:
        raise ValueError("placement mapping link mismatch")
    if placement.plan_id != plan.plan_id or placement.plan_revision != plan.plan_revision:
        raise ValueError("placement plan link mismatch")
    if placement.source_interval_ref != mapping.source_refinement_id:
        raise ValueError("placement refinement link mismatch")
    if placement.editorial_decision_ref != projected.decision_id:
        raise ValueError("placement decision link mismatch")
    if placement.timeline_domain != mapping.timeline_domain:
        raise ValueError("placement timeline domain mismatch")
    if not any(getattr(item, "placement_id", None) == placement.placement_id for item in plan.placements):
        raise ValueError("placement is not pinned by plan")
    rid = mapping.source_refinement_id
    if rid not in plan.pinned_refinements or rid not in plan.pinned_decisions:
        raise ValueError("plan authority links mismatch")
    return RealPlanArtifacts(plan, placement, mapping, projected, record["plan_digest"], record["placement_digest"], record["mapping_digest"])


__all__ = ["SourceTimelineMapping", "RealPlanArtifacts", "RealPlanLineage", "RealPlanSelection", "to_gate3_editorial_decision",
           "build_real_edit_plan", "build_fixture_plan_artifacts", "build_real_edit_plan_from_selections", "build_real_edit_plan_with_lineage",
           "build_real_edit_plan_from_selections_with_lineage", "rebind_real_plan_selections", "save_real_plan", "load_real_plan"]
