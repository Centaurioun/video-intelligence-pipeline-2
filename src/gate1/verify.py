"""Independent, fail-closed verification for the local-only Gate-1 artifact set."""
from __future__ import annotations

from datetime import datetime
import ast
import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from gate1.artifacts import (
    ARTIFACT_FILENAMES, JSONL_ARTIFACTS, ENVELOPE_OWNED_FIELDS, ArtifactError,
    contract_digest, descriptor_digest, frozen_protocol_digest, derived_run_id,
    load_artifact_root, policy_digest,
)
from gate1.canonical_json import canonical_jsonl
from gate1.contracts.validator import ContractError, validate_comparison


class VerificationError(ValueError):
    """Raised when an artifact set cannot be verified exactly."""


DEFAULT_SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas" / "gate1"
REAL_REFUSAL = "REAL execution refused: current H0 authority is synthetic-only"
_TYPES = {
    "object": lambda x: isinstance(x, Mapping), "array": lambda x: isinstance(x, list),
    "string": lambda x: isinstance(x, str),
    "integer": lambda x: isinstance(x, int) and not isinstance(x, bool),
    "number": lambda x: isinstance(x, (int, float)) and not isinstance(x, bool),
    "boolean": lambda x: isinstance(x, bool), "null": lambda x: x is None,
}
_SCHEMA_KEYWORDS = {
    "$schema", "$id", "type", "const", "enum", "required", "properties",
    "patternProperties", "additionalProperties", "items", "minItems", "maxItems",
    "uniqueItems", "minLength", "pattern", "minimum", "maximum", "minProperties",
    "oneOf", "anyOf", "format",
}
_JSON_TYPES = frozenset(_TYPES)


def _need(ok: Any, message: str) -> None:
    if not ok:
        raise VerificationError(message)


def _schema_instance(schema: Any, value: Any, where: str) -> None:
    if not isinstance(schema, Mapping):
        raise VerificationError(f"{where} schema is not an object")
    unknown = set(schema) - _SCHEMA_KEYWORDS
    _need(not unknown, f"{where} schema uses unsupported keywords {sorted(unknown)}")
    _need(schema.get("format") in (None, "date-time"),
          f"{where} schema uses unsupported format {schema.get('format')!r}")
    if "const" in schema:
        _need(value == schema["const"], f"{where} must equal {schema['const']!r}")
    if "enum" in schema:
        _need(value in schema["enum"], f"{where} is outside its schema enum")
    types = schema.get("type")
    if types is not None:
        accepted = [types] if isinstance(types, str) else types
        _need(any(_TYPES[t](value) for t in accepted), f"{where} has wrong JSON type")
        if value is None:
            # JSON Schema applies sibling constraints even when a union accepts null.
            pass
    if "oneOf" in schema:
        branches = schema["oneOf"]
        _need(isinstance(branches, list) and branches, f"{where} schema oneOf must be a non-empty array")
        matches = 0
        for branch in branches:
            try:
                _schema_instance(branch, value, where)
                matches += 1
            except VerificationError:
                pass
        _need(matches == 1, f"{where} must match exactly one oneOf branch")
    if "anyOf" in schema:
        branches = schema["anyOf"]
        _need(isinstance(branches, list) and branches, f"{where} schema anyOf must be a non-empty array")
        matches = 0
        for branch in branches:
            try:
                _schema_instance(branch, value, where)
                matches += 1
            except VerificationError:
                pass
        _need(matches >= 1, f"{where} must match at least one anyOf branch")
    if isinstance(value, Mapping):
        _need(len(value) >= schema.get("minProperties", 0), f"{where} has too few properties")
        required = schema.get("required", ())
        missing = set(required) - set(value)
        _need(not missing, f"{where} missing required fields {sorted(missing)}")
        props = schema.get("properties", {})
        patterns = schema.get("patternProperties", {})
        for key in value:
            matched = key in props
            if key in props:
                _schema_instance(props[key], value[key], f"{where}.{key}")
            for pattern, sub in patterns.items():
                if re.search(pattern, str(key)):
                    matched = True
                    _schema_instance(sub, value[key], f"{where}.{key}")
            if schema.get("additionalProperties") is False:
                _need(matched, f"{where} has undeclared field {key!r}")
            elif isinstance(schema.get("additionalProperties"), Mapping):
                _schema_instance(schema["additionalProperties"], value[key], f"{where}.{key}")
    if isinstance(value, list):
        if isinstance(schema.get("items"), Mapping):
            for i, item in enumerate(value):
                _schema_instance(schema["items"], item, f"{where}[{i}]")
        _need(len(value) >= schema.get("minItems", 0), f"{where} has too few items")
        _need(len(value) <= schema.get("maxItems", float("inf")), f"{where} has too many items")
        if schema.get("uniqueItems"):
            _need(len({json.dumps(x, sort_keys=True) for x in value}) == len(value),
                  f"{where} items are not unique")
    if isinstance(value, str):
        _need(len(value) >= schema.get("minLength", 0), f"{where} is too short")
        if "pattern" in schema:
            _need(re.search(schema["pattern"], value) is not None, f"{where} has invalid format")
        if schema.get("format") == "date-time":
            _need(bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value)),
                  f"{where} is not a date-time")
            try:
                datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise VerificationError(f"{where} is not a date-time") from None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        _need(value >= schema.get("minimum", -float("inf")), f"{where} is below minimum")
        _need(value <= schema.get("maximum", float("inf")), f"{where} is above maximum")


def _validate_schema_definition(schema: Any, where: str) -> None:
    _need(isinstance(schema, Mapping), f"{where} schema must be an object")
    unknown = set(schema) - _SCHEMA_KEYWORDS
    _need(not unknown, f"{where} schema uses unsupported keywords {sorted(unknown)}")
    if "type" in schema:
        types = schema["type"]
        types = [types] if isinstance(types, str) else types
        _need(isinstance(types, list) and bool(types) and set(types) <= _JSON_TYPES,
              f"{where} schema has unsupported type declaration")
    _need(schema.get("format") in (None, "date-time"),
          f"{where} schema uses unsupported format {schema.get('format')!r}")
    if "pattern" in schema:
        try:
            re.compile(schema["pattern"])
        except (TypeError, re.error) as exc:
            raise VerificationError(f"{where} schema has invalid pattern: {exc}") from exc
    for field in ("properties", "patternProperties"):
        if field in schema:
            _need(isinstance(schema[field], Mapping), f"{where} schema {field} must be an object")
            for key, sub in schema[field].items():
                _validate_schema_definition(sub, f"{where}.{key}")
    for field in ("items", "additionalProperties"):
        if isinstance(schema.get(field), Mapping):
            _validate_schema_definition(schema[field], f"{where}.{field}")
    for field in ("oneOf", "anyOf"):
        if field in schema:
            _need(isinstance(schema[field], list) and schema[field], f"{where} schema {field} must be a non-empty array")
            for ix, sub in enumerate(schema[field]):
                _validate_schema_definition(sub, f"{where}.{field}[{ix}]")


def verify_schemas(schema_root: Path = DEFAULT_SCHEMA_ROOT) -> None:
    root = Path(schema_root)
    try:
        registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot load schema registry: {exc}") from exc
    _need(registry.get("schema_version") == "gate1.v1", "unexpected Gate-1 schema version")
    registered = registry.get("artifacts")
    _need(isinstance(registered, list) and len(registered) == len(ARTIFACT_FILENAMES)
          and set(registered) == set(ARTIFACT_FILENAMES),
          "registry artifact closure differs from canonical closure")
    schemas = registry.get("schemas")
    _need(isinstance(schemas, Mapping) and set(schemas) == set(ARTIFACT_FILENAMES),
          "registry schema mapping does not exactly cover artifact closure")
    _need(len(set(schemas.values())) == len(ARTIFACT_FILENAMES),
          "registry must assign one unique schema file to each artifact")
    expected_files = {"registry.json", *schemas.values()}
    _need({p.name for p in root.iterdir() if p.is_file()} == expected_files,
          "Gate-1 schema directory differs from its exact registry closure")
    for artifact, filename in schemas.items():
        path = root / filename
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VerificationError(f"invalid registered schema {filename}: {exc}") from exc
        _need(schema.get("required"), f"{artifact} schema has no required fields")
        _validate_schema_definition(schema, artifact)


def _check_schemas(candidate: Mapping[str, Any], schema_root: Path | None) -> None:
    root = DEFAULT_SCHEMA_ROOT if schema_root is None else Path(schema_root)
    verify_schemas(root)
    registry = json.loads((root / "registry.json").read_text(encoding="utf-8"))
    for name in ARTIFACT_FILENAMES:
        schema = json.loads((root / registry["schemas"][name]).read_text(encoding="utf-8"))
        rows = candidate[name] if name in JSONL_ARTIFACTS else [candidate[name]]
        for i, row in enumerate(rows):
            _schema_instance(schema, row, f"{name}[{i}]" if name in JSONL_ARTIFACTS else name)


def _verify_digests(c: Mapping[str, Any]) -> None:
    m, contract = c["run_manifest.json"], c["comparison_contract.json"]
    desc, policies = c["capability_descriptors.jsonl"], c["policy_decisions.jsonl"]
    checks = (("contract_digest", contract_digest(contract)),
              ("descriptor_digest", descriptor_digest(desc)),
              ("policy_digest", policy_digest(policies)),
              ("frozen_protocol_digest", frozen_protocol_digest(contract, desc, policies, m)))
    for field, expected in checks:
        _need(m.get(field) == expected, f"{field} does not recompute exactly")
    _need(m.get("run_id") == derived_run_id(m["frozen_protocol_digest"]),
          "run_id does not derive from frozen protocol digest")


def _verify_records(c: Mapping[str, Any]) -> None:
    contract, manifest = c["comparison_contract.json"], c["run_manifest.json"]
    descriptors, policies = c["capability_descriptors.jsonl"], c["policy_decisions.jsonl"]
    _need(contract.get("execution_mode") == manifest.get("execution_mode") == "SYNTHETIC", REAL_REFUSAL)
    protocol_invalid = False
    try:
        validate_comparison(contract, descriptors, policies, manifest)
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        if str(exc) != "declared changed axis must be present and differ across arms":
            raise VerificationError(f"current D01 contract rejected artifact declarations: {exc}") from exc
        _need(manifest.get("status") == "INVALID_PROTOCOL",
              "D01 protocol failure must be marked INVALID_PROTOCOL")
        # Re-run every other D01 authority, policy, source, provenance, and
        # firewall check with a real differing descriptor axis. This narrow
        # normalization prevents the comparability exception from masking a
        # second contract failure.
        fields = (set(descriptors[0]) & set(descriptors[1])) - {"record_id", "arm_id", "policy_decision_id"}
        substitute = next((field for field in sorted(fields)
                           if descriptors[0].get(field) != descriptors[1].get(field)), None)
        _need(substitute is not None, "INVALID_PROTOCOL has no independently verifiable changed-axis declaration")
        normalized_contract = dict(contract, changed_axis=substitute)
        try:
            validate_comparison(normalized_contract, descriptors, policies, manifest)
        except (ContractError, KeyError, TypeError, ValueError) as other:
            raise VerificationError(f"current D01 contract rejected artifact declarations: {other}") from other
        protocol_invalid = True
    if not protocol_invalid:
        _need(manifest.get("status") != "INVALID_PROTOCOL",
              "INVALID_PROTOCOL status requires a recomputed D01 protocol failure")
    _need(contract["execution_mode"] == "SYNTHETIC" and manifest["execution_mode"] == "SYNTHETIC",
          REAL_REFUSAL)
    arms = set(contract["arm_ids"])
    desc_by_arm = {d["arm_id"]: d for d in descriptors}
    declared_representation = {
        (item["arm_id"], item["input_id"]): item["space_id"]
        for item in manifest["candidate_production_inputs"]
        if item["kind"] == "representation"
    }
    policy_ids = {p["policy_decision_id"] for p in policies}
    q_by_arm: dict[str, dict[str, Mapping[str, Any]]] = {arm: {} for arm in arms}
    c_by_arm: dict[str, dict[str, Mapping[str, Any]]] = {arm: {} for arm in arms}
    reprs: dict[str, set[str]] = {arm: set() for arm in arms}
    env_ids: set[str] = set()
    for ix, row in enumerate(c["embedding_results.jsonl"]):
        _need(set(row) == {"envelope", "payload"}, f"embedding row {ix} is not envelope/payload exact")
        e, p = row["envelope"], row["payload"]
        _need(not (set(p) & ENVELOPE_OWNED_FIELDS), f"embedding payload {ix} shadows envelope-owned fields")
        _need(set(e) == set(__import__("gate1.contracts.types", fromlist=["BenchmarkEnvelope"]).BenchmarkEnvelope.__dataclass_fields__),
              f"embedding envelope {ix} does not match the current D01 type")
        _need(e["record_id"] not in env_ids, "duplicate embedding record_id")
        env_ids.add(e["record_id"])
        arm = e["arm_id"]
        _need(arm in arms, f"embedding arm {arm!r} is undeclared")
        desc = desc_by_arm[arm]
        _need(e["comparison_id"] == contract["comparison_id"] and e["run_id"] == manifest["run_id"],
              "embedding envelope comparison/run reference mismatch")
        _need(e["policy_decision_id"] in policy_ids, "embedding policy reference does not resolve")
        _need(e["policy_decision_id"] == desc["policy_decision_id"], "embedding policy differs from descriptor")
        _need(e["request_ref"] is None and e["raw_response_artifact_ref"] is None,
              "synthetic candidate record cannot claim a provider request or response")
        _need(not e["judgment_version_refs"], "candidate-production envelope cannot reference evaluation judgments")
        _need(e["validity_ref"] is None and e["outcome_ref"] is None,
              "candidate-production envelope cannot claim evaluation output references")
        _need(e["wall_time_ms"] is None and all(v == "NOT_OBSERVED" for v in e["resource_observations"].values()),
              "synthetic candidate record cannot claim measured runtime/resource observations")
        for field in ("requested_model", "resolved_backend", "config_digest"):
            _need(e[field] == desc[field], f"embedding {field} differs from its descriptor")
        _need(p["space_id"] == desc["space_id"], "embedding space does not match arm descriptor")
        _need(p["representation_id"] not in reprs[arm], "duplicate representation in one arm")
        reprs[arm].add(p["representation_id"])
        kind = p["kind"]
        _need(e["input_refs"] == [p["representation_id"]],
              "embedding input reference does not resolve exactly to its retained representation")
        _need(declared_representation.get((arm, p["representation_id"])) == p["space_id"],
              "embedding input reference representation arm/space does not resolve")
        coverage = e["consumed_coverage"]
        consumed = int(p["vector"] is not None)
        _need(coverage.get("expected") == 1 and coverage.get("consumed") == consumed,
              "embedding consumed coverage does not match its retained input")
        omitted = coverage.get("omitted", 0)
        failed = coverage.get("failed", 0)
        _need(omitted + failed == 1 - consumed,
              "embedding consumed coverage omission/failure counts do not reconcile")
        _need((kind == "query" and p["query_id"] and p["candidate_id"] is None) or
              (kind == "candidate" and p["candidate_id"] and p["query_id"] is None),
              "embedding payload key does not match its kind")
        store = q_by_arm[arm] if kind == "query" else c_by_arm[arm]
        key = p["query_id"] if kind == "query" else p["candidate_id"]
        _need(key not in store, f"duplicate {kind} input {key!r} for arm {arm}")
        store[key] = row
        if p["vector"] is not None:
            v = p["vector"]
            _need(isinstance(v, list) and len(v) > 0 and all(type(x) in (int, float) and math.isfinite(x) for x in v),
                  "vector must contain finite numeric values")
            _need(abs(math.sqrt(sum(x*x for x in v)) - 1.0) <= 1e-9, "vector is not normalized")
    _need(set(q_by_arm[contract["arm_ids"][0]]) == set(q_by_arm[contract["arm_ids"][1]]),
          "query identities differ across arms")
    _need(set(c_by_arm[contract["arm_ids"][0]]) == set(c_by_arm[contract["arm_ids"][1]]),
          "candidate identities differ across arms")
    declared_inputs = manifest["candidate_production_inputs"]
    observed_inputs = set()
    observed_inputs.update(("query", key) for key in q_by_arm[contract["arm_ids"][0]])
    observed_inputs.update(("candidate", key) for key in c_by_arm[contract["arm_ids"][0]])
    for arm, keys in reprs.items():
        observed_inputs.update(("representation", arm, key) for key in keys)
    declared_keys = set()
    for item in declared_inputs:
        if item["kind"] == "representation":
            declared_keys.add(("representation", item["arm_id"], item["input_id"]))
        else:
            declared_keys.add((item["kind"], item["input_id"]))
    _need(declared_keys == observed_inputs,
          "candidate_production_inputs do not exactly match retained embedding inputs")
    query_ids = set(q_by_arm[contract["arm_ids"][0]])
    candidate_ids = set(c_by_arm[contract["arm_ids"][0]])
    for row in c["ranked_candidates.jsonl"]:
        _need(row["arm_id"] in arms and row["query_id"] in query_ids and row["candidate_id"] in candidate_ids,
              "ranking has unresolved arm/query/candidate reference")
        _need(row["representation_id"] in reprs[row["arm_id"]] and
              row["space_id"] == desc_by_arm[row["arm_id"]]["space_id"], "ranking representation/space does not resolve")
    for j in c["judgments.jsonl"]:
        _need(j["query_id"] in query_ids and j["candidate_id"] in candidate_ids,
              "judgment query/candidate reference does not resolve")
        _need(j["synthetic"] is True, "non-synthetic judgment is outside this evidence boundary")
    _need(c["benchmark_report.json"]["comparison_id"] == contract["comparison_id"], "report comparison does not resolve")
    _need(manifest["provenance"]["run_id"] == manifest["run_id"], "provenance run_id mismatch")


def _independent_rankings(c: Mapping[str, Any]) -> list[dict[str, Any]]:
    contract = c["comparison_contract.json"]
    grouped: dict[str, dict[str, dict[str, Mapping[str, Any]]]] = {}
    for row in c["embedding_results.jsonl"]:
        e, p = row["envelope"], row["payload"]
        grouped.setdefault(e["arm_id"], {"query": {}, "candidate": {}})[p["kind"]][p["query_id"] if p["kind"] == "query" else p["candidate_id"]] = row
    expected = []
    for arm in contract["arm_ids"]:
        data = grouped.get(arm, {"query": {}, "candidate": {}})
        for qid, qrow in sorted(data["query"].items()):
            qv = qrow["payload"]["vector"]
            if qv is None:
                raise VerificationError(f"query {qid} has no vector for deterministic ranking")
            scored, failed = [], []
            for cid, crow in sorted(data["candidate"].items()):
                cv = crow["payload"]["vector"]
                p = crow["payload"]
                base = dict(record_id=f"rank-{arm}-{qid}-{cid}", arm_id=arm, query_id=qid,
                            candidate_id=cid, representation_id=p["representation_id"], space_id=p["space_id"])
                if cv is None:
                    failure_evidence = (
                        bool(p.get("failure_reason"))
                        or crow["envelope"].get("provider_status") in {"FAILED", "PARTIAL"}
                        or bool(crow["envelope"].get("per_item_errors"))
                    )
                    failed.append({**base, "score": None, "rank": None, "tie_key": None,
                                   "coverage_status": "FAILED" if failure_evidence else "OMITTED"})
                else:
                    _need(len(qv) == len(cv), "query and candidate vector dimensions differ")
                    score = sum(float(a)*float(b) for a,b in zip(qv,cv))
                    scored.append((score, cid.encode("utf-8"), base))
            scored.sort(key=lambda x: (-x[0], x[1]))
            for rank, (score, tie, base) in enumerate(scored, 1):
                expected.append({**base, "score": score, "rank": rank, "tie_key": [-score, tie.decode("utf-8")], "coverage_status": "SELECTED"})
            expected.extend(failed)
    return sorted(expected, key=lambda row: row["record_id"])


def _independent_report(c: Mapping[str, Any]) -> dict[str, Any]:
    contract = c["comparison_contract.json"]
    rankings, judgments = c["ranked_candidates.jsonl"], c["judgments.jsonl"]
    metric = contract["primary_metric"]
    try:
        k = int(metric["k"])
        min_delta = float(metric["min_delta"])
    except (KeyError, TypeError, ValueError) as exc:
        raise VerificationError("primary metric must declare integer k and numeric min_delta") from exc
    _need(k > 0, "primary metric k must be positive")
    arm_ids = contract["arm_ids"]
    query_ids = sorted({row["query_id"] for row in rankings})
    _need(bool(query_ids), "rankings must retain at least one query for evaluation")
    relevant = {(j["query_id"], j["candidate_id"]) for j in judgments if j["relevant"]}
    arm_values: dict[str, float] = {}
    coverage: dict[str, int] = {}
    incomplete = False
    for arm in arm_ids:
        arm_rows = [row for row in rankings if row["arm_id"] == arm]
        coverage[arm] = sum(row["coverage_status"] == "SELECTED" for row in arm_rows)
        incomplete |= any(row["coverage_status"] != "SELECTED" for row in arm_rows)
        hits = 0
        for query_id in query_ids:
            hits += any(row["arm_id"] == arm and row["query_id"] == query_id
                        and row["coverage_status"] == "SELECTED" and row["rank"] is not None
                        and row["rank"] <= k and (query_id, row["candidate_id"]) in relevant
                        for row in rankings)
        arm_values[arm] = hits / len(query_ids)
    delta = arm_values[arm_ids[1]] - arm_values[arm_ids[0]]
    failure_event = c["failure_ledger.json"]["event_type"]
    protocol_invalid = c["run_manifest.json"].get("status") == "INVALID_PROTOCOL"
    if protocol_invalid:
        status, failure_class = "INVALID_PROTOCOL", None
        validity, primary_value = "INVALID_PROTOCOL", None
        conclusion = "COMPARISON_INVALID_NO_OUTCOME_CLAIM"
    elif failure_event == "RESOURCE_OPERABILITY":
        status, failure_class = "FAIL", "RESOURCE_OPERABILITY"
        validity, primary_value = "VALID", delta
        conclusion = "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
    elif metric.get("require_complete_coverage", False) and incomplete:
        status, failure_class = "FAIL", "COVERAGE_INCOMPLETE"
        validity, primary_value = "VALID", delta
        conclusion = "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
    elif delta >= min_delta:
        status, failure_class = "PASS", None
        validity, primary_value = "VALID", delta
        conclusion = "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
    else:
        status, failure_class = "FAIL", "QUALITY"
        validity, primary_value = "VALID", delta
        conclusion = "SYNTHETIC_ONLY_NO_REAL_WINNER_OR_PROMOTION_CLAIM"
    return {
        "comparison_id": contract["comparison_id"], "validity": validity,
        "benchmark_status": status, "primary_metric_id": metric["metric_id"],
        "primary_value": primary_value, "arm_values": arm_values, "coverage": coverage,
        "failure_class": failure_class,
        "conclusion": conclusion,
    }


def _verify_receipt(c: Mapping[str, Any]) -> None:
    m, receipt = c["run_manifest.json"], c["synthetic_receipt.json"]
    _need(receipt["execution_mode"] == "SYNTHETIC", "receipt must state SYNTHETIC mode")
    expected = {"real_benchmark_executed": False, "provider_calls": 0, "network_egress_bytes": 0,
                "protected_media_used": False, "model_download_or_change": False,
                "winner_observed": False, "real_model_provider_claims": "NOT_OBSERVED",
                "gate0_terminal_sha": None, "gate_promotion": False}
    for field, value in expected.items():
        _need(receipt.get(field) == value, f"synthetic receipt must state {field}={value!r}")
    for field in ("spec_sha", "execution_authority_sha", "canonical_contract_blob"):
        _need(receipt[field] == m[field], f"receipt {field} mismatch")


def verify_artifact_set(candidate: Mapping[str, Any], *, mode: str = "SYNTHETIC", schema_root: Path | None = None) -> None:
    if mode == "REAL":
        raise VerificationError(REAL_REFUSAL)
    _need(mode == "SYNTHETIC", f"unknown verification mode {mode!r}")
    _need(isinstance(candidate, Mapping) and set(candidate) == set(ARTIFACT_FILENAMES),
          "candidate must contain exactly the canonical ten artifact files")
    for name in ARTIFACT_FILENAMES:
        if name in JSONL_ARTIFACTS:
            _need(isinstance(candidate[name], list), f"{name} must be an ordered record list")
            try:
                canonical_jsonl(candidate[name])
            except (TypeError, ValueError) as exc:
                raise VerificationError(f"{name} is not canonical ordered JSONL: {exc}") from exc
        else:
            _need(isinstance(candidate[name], Mapping), f"{name} must be an object")
    _check_schemas(candidate, schema_root)
    _verify_digests(candidate)
    _verify_records(candidate)
    _need(candidate["run_manifest.json"]["execution_mode"] == "SYNTHETIC", REAL_REFUSAL)
    _need(candidate["run_manifest.json"]["status"] in {"PLANNED", "VALID", "INVALID_PROTOCOL", "NOT_RUN"},
          "synthetic run status cannot claim an execution outcome")
    expected = _independent_rankings(candidate)
    _need(candidate["ranked_candidates.jsonl"] == expected,
          "ranking rows differ from independent exact recomputation")
    _need(candidate["benchmark_report.json"] == _independent_report(candidate),
          "benchmark_report.json differs from independent synthetic-only report recomputation")
    ledger, manifest = candidate["failure_ledger.json"], candidate["run_manifest.json"]
    _need(ledger["run_id"] == manifest["run_id"] and ledger["comparison_id"] == manifest["comparison_id"],
          "failure ledger run/comparison reference mismatch")
    _need(ledger["attempt_id"] == manifest["provenance"].get("attempt_id"), "failure ledger attempt mismatch")
    fault = manifest["synthetic_fault"]
    _need((fault == "NONE" and ledger["event_type"] == "NONE") or
          (fault == "RESOURCE_OPERABILITY" and ledger["event_type"] == "RESOURCE_OPERABILITY"),
          "failure ledger event does not match frozen synthetic fault")
    if ledger["event_type"] == "NONE":
        _need(not ledger["affected_refs"], "NONE failure ledger event cannot name affected records")
    else:
        _need(bool(ledger["affected_refs"]), "failure ledger event must identify affected records")
        env_ids = {row["envelope"]["record_id"] for row in candidate["embedding_results.jsonl"]}
        _need(set(ledger["affected_refs"]) <= env_ids,
              "failure ledger affected record references do not resolve")
    _verify_receipt(candidate)


def verify_path(path: Path, *, mode: str = "SYNTHETIC") -> None:
    if mode == "REAL":
        raise VerificationError(REAL_REFUSAL)
    root = Path(path)
    if root.is_dir() and any((root / name).exists() for name in THREE_ARM_ARTIFACT_FILENAMES):
        verify_three_arm_path(root, mode=mode)
        return
    try:
        candidate = load_artifact_root(root)
    except ArtifactError as exc:
        raise VerificationError(str(exc)) from exc
    verify_artifact_set(candidate, mode=mode)


THREE_ARM_REPORT_FILENAME = "three_arm_compat_report.json"
THREE_ARM_RECEIPT_FILENAME = "three_arm_compat_receipt.json"
THREE_ARM_ARTIFACT_FILENAMES = (THREE_ARM_REPORT_FILENAME, THREE_ARM_RECEIPT_FILENAME)
_THREE_ARM_ARMS = ("VIP_V1_BASE", "VIP_V2_BASE", "VIP_V2_SO400M")
_THREE_ARM_PAIRS = (
    (_THREE_ARM_ARMS[0], _THREE_ARM_ARMS[1]),
    (_THREE_ARM_ARMS[0], _THREE_ARM_ARMS[2]),
    (_THREE_ARM_ARMS[1], _THREE_ARM_ARMS[2]),
)
_THREE_ARM_REPORT_FIELDS = frozenset({
    "schema_version", "execution_mode", "fixture_id", "code_sha", "contract_digest",
    "evidence_status", "judgment_evidence_class", "evaluation_scope",
    "operational_evaluation_status", "compatibility_status", "benchmark_readiness",
    "pairwise_evaluations", "b07_metric_states", "arm_derivations", "winner_status",
    "limitations",
})
_THREE_ARM_PAIR_FIELDS = frozenset({
    "arm_ids", "comparison_id", "validity", "benchmark_status", "outcome",
    "primary_metric_id", "primary_value", "arm_values", "coverage", "failure_class",
    "conclusion",
})
_THREE_ARM_RECEIPT_FIELDS = frozenset({
    "schema_version", "execution_mode", "fixture_id", "evidence_status",
    "judgment_evidence_class", "code_sha", "contract_digest", "compat_contract",
    "report_filename", "report_sha256", "claim_limits", "real_benchmark_executed",
    "provider_calls", "network_egress_bytes", "protected_media_used",
    "model_download_or_change", "winner_observed", "gate_promotion",
})
_THREE_ARM_LIMITATIONS = [
    "SYNTHETIC_PROTOCOL_COMPATIBILITY_ONLY",
    "NOT_OPERATIONAL_THREE_ARM_B00_B18_EVALUATION",
    "NO_MODEL_EVIDENCE",
    "NO_WINNER_SELECTION",
    "NO_GATE1_PROMOTION",
]
_THREE_ARM_CONCLUSIONS = frozenset({
    "COMPARISON_INVALID_NO_OUTCOME_CLAIM",
    "SYNTHETIC_VALID_NEGATIVE_EVIDENCE",
    "SYNTHETIC_DELTA_MEETS_CONFIGURED_THRESHOLD",
    "SYNTHETIC_DELTA_BELOW_CONFIGURED_THRESHOLD",
})
_THREE_ARM_FAILURE_CLASSES = frozenset({None, "RESOURCE_OPERABILITY",
                                        "COVERAGE_INCOMPLETE", "QUALITY"})
_THREE_ARM_DERIVATION_SOURCES = ("arm_a", "arm_b", "arm_b")
_THREE_ARM_B07_REASONS = {
    "recall_at_5": "POOLED_GROUND_TRUTH",
    "ndcg_at_10": "METRIC_NOT_IMPLEMENTED",
}
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_COVERAGE_KEY = re.compile(r"^[A-Za-z0-9._:-]+::(SELECTED|FAILED|OMITTED|QUARANTINED)$")


def _three_arm_canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _three_arm_coverage(pair: Mapping[str, Any]) -> None:
    coverage = pair["coverage"]
    _need(isinstance(coverage, Mapping) and len(coverage) >= 2,
          "three-arm pair coverage must be a non-trivial object")
    for key, value in coverage.items():
        _need(isinstance(key, str) and bool(_COVERAGE_KEY.match(key)),
              f"three-arm coverage key is not a typed arm status: {key!r}")
        _need(isinstance(value, int) and not isinstance(value, bool) and value >= 0,
              f"three-arm coverage count must be a non-negative integer: {key!r}")


def _verify_three_arm_pair(pair: Any, expected_pair: tuple[str, str]) -> None:
    _need(isinstance(pair, Mapping) and set(pair) == _THREE_ARM_PAIR_FIELDS,
          "three-arm pair evaluation fields are not the frozen set")
    _need(tuple(pair["arm_ids"]) == expected_pair,
          "three-arm pairs must follow the exact frozen charter pair order")
    _need(isinstance(pair["comparison_id"], str) and pair["comparison_id"],
          "three-arm pair comparison_id must be a non-empty string")
    _need(pair["primary_metric_id"] == "macro_hit_at_1",
          "three-arm pair primary metric must be macro_hit_at_1")
    _three_arm_coverage(pair)
    _need(pair["failure_class"] in _THREE_ARM_FAILURE_CLASSES,
          "three-arm pair failure_class is outside the frozen vocabulary")
    _need(pair["conclusion"] in _THREE_ARM_CONCLUSIONS,
          "three-arm pair conclusion is outside the frozen vocabulary")
    validity = pair["validity"]
    _need(validity in {"VALID", "INVALID_PROTOCOL"}, "three-arm pair validity is unknown")
    if validity == "VALID":
        _need(pair["benchmark_status"] in {"PASS", "FAIL"},
              "a valid three-arm pair must carry a PASS/FAIL benchmark outcome")
        _need(pair["outcome"] == pair["benchmark_status"],
              "three-arm pair outcome must equal its benchmark status when valid")
        _need(isinstance(pair["primary_value"], (int, float))
              and not isinstance(pair["primary_value"], bool),
              "a valid three-arm pair must carry a numeric primary value")
        arm_values = pair["arm_values"]
        _need(isinstance(arm_values, Mapping) and set(arm_values) == set(expected_pair),
              "three-arm pair arm_values must cover exactly its two arms")
        _need(all(isinstance(value, (int, float)) and not isinstance(value, bool)
                  for value in arm_values.values()),
              "three-arm pair arm_values must be numeric")
    else:
        _need(pair["benchmark_status"] == "INVALID_PROTOCOL",
              "an invalid three-arm protocol must not carry a benchmark outcome")
        _need(pair["outcome"] == "NOT_EVALUATED",
              "an invalid three-arm protocol outcome is NOT_EVALUATED")
        _need(pair["primary_value"] is None, "an invalid three-arm pair has no primary value")
        _need(pair["arm_values"] == {}, "an invalid three-arm pair has no arm values")
        _need(pair["failure_class"] is None, "an invalid three-arm pair has no failure class")
        _need(pair["conclusion"] == "COMPARISON_INVALID_NO_OUTCOME_CLAIM",
              "an invalid three-arm pair must not claim an outcome conclusion")


def _verify_three_arm_report(report: Any) -> None:
    _need(isinstance(report, Mapping) and set(report) == _THREE_ARM_REPORT_FIELDS,
          "three-arm report fields are not the frozen set")
    _need(report["schema_version"] == 2 and report["execution_mode"] == "SYNTHETIC",
          "three-arm report must declare synthetic schema version 2")
    _need(report["evidence_status"] == "SYNTHETIC_NOT_MODEL_EVIDENCE",
          "three-arm report must not claim model evidence")
    _need(report["judgment_evidence_class"] == "NOT_APPLICABLE_SYNTHETIC",
          "three-arm report judgments must be non-applicable synthetic evidence")
    _need(report["evaluation_scope"] == "SYNTHETIC_PROTOCOL_COMPATIBILITY_ONLY",
          "three-arm report scope must be synthetic protocol compatibility only")
    _need(report["operational_evaluation_status"] == "NOT_IMPLEMENTED",
          "operational three-arm B00-B18 evaluation is not implemented")
    _need(report["compatibility_status"] == "COMPATIBLE",
          "three-arm report compatibility_status must be COMPATIBLE")
    _need(report["benchmark_readiness"] == "NOT_BENCHMARK_READY",
          "three-arm report must not claim benchmark readiness")
    _need(report["winner_status"] == "NOT_EVALUATED", "three-arm report must not select a winner")
    _need(report["limitations"] == _THREE_ARM_LIMITATIONS,
          "three-arm report limitations are not the frozen synthetic-only list")
    _need(isinstance(report["fixture_id"], str) and report["fixture_id"],
          "three-arm report fixture_id must be a non-empty generated case id")
    _need(isinstance(report["code_sha"], str) and bool(_HEX64.match(report["code_sha"])),
          "three-arm report code_sha must be a deterministic sha256 digest")
    _need(isinstance(report["contract_digest"], str)
          and bool(_HEX64.match(report["contract_digest"])),
          "three-arm report contract_digest must be a sha256 digest")

    derivations = report["arm_derivations"]
    _need(isinstance(derivations, list) and len(derivations) == len(_THREE_ARM_ARMS),
          "three-arm report must record exactly one derivation per charter arm")
    for index, row in enumerate(derivations):
        _need(isinstance(row, Mapping)
              and set(row) == {"arm_id", "derived_from_arm_id", "synthetic_projection"},
              "three-arm derivation record fields are not the frozen set")
        _need(row["arm_id"] == _THREE_ARM_ARMS[index],
              "three-arm derivations must follow the frozen charter order")
        _need(row["derived_from_arm_id"] == _THREE_ARM_DERIVATION_SOURCES[index],
              "three-arm derivation source arm is not the charter source for that arm")
        _need(row["synthetic_projection"] is (index == len(_THREE_ARM_ARMS) - 1),
              "only the third charter arm may be a synthetic projection")

    states = report["b07_metric_states"]
    _need(isinstance(states, list) and len(states) == len(_THREE_ARM_B07_REASONS),
          "three-arm report must state exactly the two B07 NOT_COMPUTABLE metrics")
    _need(all(isinstance(state, Mapping) for state in states),
          "B07 metric states must be objects")
    _need({state.get("metric_id") for state in states} == set(_THREE_ARM_B07_REASONS),
          "B07 metric states must cover exactly the implemented-gap metric ids, without duplicates")
    for state in states:
        _need(isinstance(state, Mapping)
              and set(state) == {"metric_id", "status", "reason"},
              "B07 metric state fields are not the frozen set")
        metric_id = state["metric_id"]
        _need(metric_id in _THREE_ARM_B07_REASONS and state["status"] == "NOT_COMPUTABLE",
              "B07 metric states must be known NOT_COMPUTABLE metrics")
        _need(state["reason"] == _THREE_ARM_B07_REASONS[metric_id],
              "B07 metric reason must name the real implemented gap")

    pairs = report["pairwise_evaluations"]
    _need(isinstance(pairs, list) and len(pairs) == len(_THREE_ARM_PAIRS),
          "three-arm report must contain exactly the three frozen charter pairs")
    for pair, expected_pair in zip(pairs, _THREE_ARM_PAIRS):
        _verify_three_arm_pair(pair, expected_pair)


def _verify_three_arm_receipt(receipt: Any, report: Mapping[str, Any],
                              report_bytes: bytes) -> None:
    _need(isinstance(receipt, Mapping) and set(receipt) == _THREE_ARM_RECEIPT_FIELDS,
          "three-arm receipt fields are not the frozen set")
    _need(receipt["schema_version"] == 2 and receipt["execution_mode"] == "SYNTHETIC",
          "three-arm receipt must declare synthetic schema version 2")
    _need(receipt["evidence_status"] == "SYNTHETIC_NOT_MODEL_EVIDENCE",
          "three-arm receipt must not claim model evidence")
    _need(receipt["judgment_evidence_class"] == "NOT_APPLICABLE_SYNTHETIC",
          "three-arm receipt judgments must be non-applicable synthetic evidence")
    _need(receipt["fixture_id"] == report["fixture_id"],
          "three-arm receipt fixture_id does not match the report")
    _need(receipt["code_sha"] == report["code_sha"],
          "three-arm receipt code_sha does not match the report")
    _need(receipt["contract_digest"] == report["contract_digest"],
          "three-arm receipt contract_digest does not match the report")
    _need(receipt["report_filename"] == THREE_ARM_REPORT_FILENAME,
          "three-arm receipt must name the canonical report filename")
    _need(receipt["report_sha256"] == hashlib.sha256(report_bytes).hexdigest(),
          "three-arm receipt does not bind the exact report bytes")
    contract = receipt["compat_contract"]
    _need(isinstance(contract, Mapping), "three-arm receipt must embed the compatibility contract")
    _need(contract_digest(contract) == report["contract_digest"],
          "three-arm receipt compatibility contract does not match the report digest")
    _need(receipt["claim_limits"] == _THREE_ARM_LIMITATIONS,
          "three-arm receipt claim limits are not the frozen synthetic-only list")
    expected = {"real_benchmark_executed": False, "provider_calls": 0,
                "network_egress_bytes": 0, "protected_media_used": False,
                "model_download_or_change": False, "winner_observed": False,
                "gate_promotion": False}
    for field, value in expected.items():
        _need(receipt.get(field) == value,
              f"three-arm receipt must state {field}={value!r}")


def verify_three_arm_path(path: Path, *, mode: str = "SYNTHETIC") -> None:
    if mode == "REAL":
        raise VerificationError(REAL_REFUSAL)
    _need(mode == "SYNTHETIC", f"unknown verification mode {mode!r}")
    root = Path(path)
    _need(root.is_dir(), f"three-arm artifact root does not exist: {root}")
    present = {entry.name for entry in root.iterdir()}
    missing = sorted(set(THREE_ARM_ARTIFACT_FILENAMES) - present)
    extra = sorted(present - set(THREE_ARM_ARTIFACT_FILENAMES))
    _need(not missing and not extra,
          f"three-arm artifact closure mismatch; missing={missing} extra={extra}")
    report_bytes = (root / THREE_ARM_REPORT_FILENAME).read_bytes()
    receipt_bytes = (root / THREE_ARM_RECEIPT_FILENAME).read_bytes()
    try:
        report = json.loads(report_bytes)
        receipt = json.loads(receipt_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"three-arm artifact is not valid JSON: {exc}") from exc
    _need(_three_arm_canonical_bytes(report) == report_bytes,
          "three-arm report bytes are not canonical deterministic JSON")
    _need(_three_arm_canonical_bytes(receipt) == receipt_bytes,
          "three-arm receipt bytes are not canonical deterministic JSON")
    _verify_three_arm_report(report)
    _verify_three_arm_receipt(receipt, report, report_bytes)


def verify_synthetic_only(repo_root: Path) -> None:
    forbidden = {"requests", "httpx", "aiohttp", "urllib", "socket", "openai", "anthropic",
                 "google", "boto3", "torch", "transformers", "sentence_transformers",
                 "qdrant_client", "lancedb", "numpy", "scipy"}
    source_root = Path(repo_root) / "src" / "gate1"
    for source in sorted(source_root.rglob("*.py")):
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError) as exc:
            raise VerificationError(f"cannot inspect synthetic source {source}: {exc}") from exc
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module: roots.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"__import__", "import_module"} and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str): roots.add(node.args[0].value.split(".")[0])
        _need(not roots & forbidden, f"{source} imports forbidden runtime modules {sorted(roots & forbidden)}")
        _need("tests" not in roots, f"{source} imports the test package")
    for name in (".env", ".env.local", ".env.production", "credentials.json", "models", "model_weights", "media", "videos", "qdrant_storage"):
        _need(not (Path(repo_root) / name).exists(), f"prohibited runtime/credential path exists: {name}")
