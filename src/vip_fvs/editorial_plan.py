"""Editorial decision and edit-plan bridge for the local FVS.

This module deliberately contains no renderer logic.  It turns a refined candidate into
the Gate-3 plan model only after an explicit human (or synthetic-human fixture) decision,
and preserves the evidence/source/policy identities required by that model.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def editorial_decision(
    *,
    decision_id: str,
    principal_kind: str,
    principal_ref: str,
    refinement_id: str,
    plan_revision: int,
    decision_class: str = "ACCEPT",
    rationale: str,
    options_considered: Sequence[str] = (),
    fixture_scope: str | None = None,
    presentation_manifest_ref: str | None = None,
) -> Any:
    """Create the only decision type admitted by Gate-3's plan constructor.

    A model/tool principal is intentionally rejected by ``gate3.editorial``.  Synthetic
    decisions must identify their fixture scope; this keeps a structurally valid fixture
    plan visibly non-production.
    """
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("an explicit editorial rationale is required")
    if principal_kind == "SYNTHETIC_HUMAN" and fixture_scope != "SYNTHETIC_FIXTURE":
        raise ValueError("synthetic-human decisions require fixture scope SYNTHETIC_FIXTURE")
    from gate3.editorial import EditorialDecision

    return EditorialDecision(
        decision_id,
        principal_kind,
        principal_ref,
        refinement_id,
        plan_revision,
        decision_class,
        rationale.strip(),
        list(options_considered),
        presentation_manifest_ref=presentation_manifest_ref,
        fixture_scope=fixture_scope,
    )


def build_edit_plan(
    *,
    plan_id: str,
    plan_revision: int,
    refinement: Mapping[str, Any],
    decision: Any,
    placements: Sequence[Any],
    source_revision_ids: Sequence[str],
    policy_decision_ref: str | None = None,
    plan_scope: str = "SYNTHETIC_FIXTURE",
    pinned_source_digest: str | None = None,
) -> Any:
    """Build a versioned Gate-3 plan with all authority pins explicit.

    ``EditPlanRevision`` performs the authoritative refinement, decision, and overlap
    checks.  This bridge supplies its maps and refuses ambiguous/missing identity pins
    before construction.  Synthetic plans remain structurally useful but cannot become
    export eligible under the Gate-3 model.
    """
    if not isinstance(refinement, Mapping):
        raise TypeError("refinement must be a mapping")
    refinement_id = refinement.get("refinement_id")
    evidence_digest = refinement.get("evidence_digest")
    if not isinstance(refinement_id, str) or not refinement_id:
        raise ValueError("refinement_id is required")
    if not isinstance(evidence_digest, str) or not evidence_digest:
        raise ValueError("evidence_digest is required")
    if decision is None:
        raise ValueError("an explicit editorial decision is required")
    if getattr(decision, "decided_on_refinement", None) != refinement_id:
        raise ValueError("decision must bind the selected refinement")
    if not source_revision_ids:
        raise ValueError("source revision identity is required")
    if plan_scope == "SYNTHETIC_FIXTURE":
        if getattr(decision, "principal_kind", None) != "SYNTHETIC_HUMAN":
            raise ValueError("synthetic plans require a synthetic-human decision")
        if getattr(decision, "fixture_scope", None) != "SYNTHETIC_FIXTURE":
            raise ValueError("synthetic plans require fixture-scoped decisions")
    if pinned_source_digest is not None:
        declared = refinement.get("source_content_digest")
        if declared != pinned_source_digest:
            raise ValueError("source digest pin does not match refinement")

    from gate3.plan import EditPlanRevision

    # A fixture-addressed human-shaped decision is useful for structural tests,
    # but it is not real editorial authority. Downgrade it to the explicit
    # synthetic scope so Gate-3 cannot accidentally make it export eligible.
    effective_scope = plan_scope
    effective_decision = decision
    if (plan_scope == "REAL" and getattr(decision, "principal_kind", None) != "SYNTHETIC_HUMAN"
            and not bool(getattr(decision, "real_authority_eligible", False))):
        effective_scope = "SYNTHETIC_FIXTURE"
        # Gate-3's structural synthetic scope requires an explicitly synthetic
        # principal. Preserve the caller's non-authoritative decision object,
        # but pin a synthetic projection so it cannot confer real authority.
        try:
            from dataclasses import replace
            effective_decision = replace(decision, principal_kind="SYNTHETIC_HUMAN", fixture_scope="SYNTHETIC_FIXTURE")
        except (TypeError, ValueError):
            effective_decision = decision

    return EditPlanRevision(
        plan_id,
        plan_revision,
        list(placements),
        {refinement_id: dict(refinement)},
        {refinement_id: effective_decision},
        list(source_revision_ids),
        plan_scope=effective_scope,
        policy_decision_ref=policy_decision_ref,
        pinned_evidence_digests={refinement_id: evidence_digest},
    )


# Descriptive aliases used by the coordinator and downstream tests.
create_editorial_decision = editorial_decision
create_edit_plan = build_edit_plan


__all__ = [
    "build_edit_plan",
    "create_edit_plan",
    "create_editorial_decision",
    "editorial_decision",
]
