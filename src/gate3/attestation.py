def build_fixture_attestation(fixture_id,principal_kind,recipe_ref,recipe_digest,oracle_refs,*,fixture_scope="SYNTHETIC_FIXTURE",not_observed=()):
    if fixture_scope!="SYNTHETIC_FIXTURE":raise ValueError("fixture_scope must be SYNTHETIC_FIXTURE")
    if principal_kind not in ("SYNTHETIC_HUMAN","DETERMINISTIC_TOOL"):raise ValueError("unknown principal kind")
    return {"fixture_id":fixture_id,"fixture_scope":fixture_scope,"principal_kind":principal_kind,"production_eligible":False,"real_authority_eligible":False,"generated_from_recipe_ref":recipe_ref,"recipe_digest":recipe_digest,"oracle_refs":list(oracle_refs),"NOT_OBSERVED":list(not_observed)}
