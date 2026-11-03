def build_presentation_manifest(*,shown,visible_scores,ordering_policy,tie_break_policy):
    if not tie_break_policy:raise ValueError("tie-break required")
    return {"shown":list(shown),"order":list(shown),"visible_scores":dict(visible_scores),"ordering_policy":ordering_policy,"tie_break_policy":tie_break_policy,"scores_authority":"NONE","derived_evidence_class":"EDITORIAL_INFERENCE"}
