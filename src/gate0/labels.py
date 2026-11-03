"""Typed pre-ranking query/gold label construction with a blinded rank boundary."""
from __future__ import annotations
from fractions import Fraction
from typing import Iterable, Mapping
from gate0.canonical_json import canonical_bytes
from gate0.contracts.types import record_digest
from gate0.identity import digest_bytes, digest_json, opaque_id

FAMILIES = {"APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT"}
PRESENCE = {"POSITIVE", "ABSENT"}
# CANONICAL_CONTRACTS.md §4: the eight typed time domains. Reviewer-declared
# semantic intervals default to SEMANTIC_SECONDS; any other spelling (including
# the non-canonical NORMALIZED_PTS) is rejected rather than coerced.
CANONICAL_TIME_DOMAINS = frozenset({
    "SEMANTIC_SECONDS",
    "TECHNICAL_WINDOW",
    "MATCHED_OFFSET",
    "SOURCE_PTS",
    "SOURCE_FRAME",
    "PROXY_TIME",
    "TIMELINE_TIME",
    "RENDERED_OUTPUT",
})
DEFAULT_GOLD_TIME_DOMAIN = "SEMANTIC_SECONDS"

def label_version_digest(records: Iterable[Mapping]) -> str:
    return digest_bytes(canonical_bytes(sorted((dict(row) for row in records), key=lambda row: str(row.get("query_id", row.get("assertion_id", ""))))))

def _record(kind, payload, prefix):
    row = {"record_id": opaque_id(prefix, payload), "record_type": kind, "record_schema_version": "gate0.v1", "record_digest": "", "payload": payload}
    row["record_digest"] = record_digest(row)
    return row

def build_queries(specs: Iterable[tuple[str, str, tuple[str, str]]], split_by_id: Mapping[str, str], query_version: str) -> tuple[dict, ...]:
    specs = tuple(specs)
    if len(specs) != 40: raise ValueError("expected exactly 40 queries")
    rows = []
    for query_id, text, (family, presence) in specs:
        split = split_by_id.get(query_id)
        if not text or family not in FAMILIES or presence not in PRESENCE or split not in {"DEVELOPMENT", "EVALUATION"}: raise ValueError("invalid query")
        payload = {"query_id": str(query_id), "text": str(text), "family": family, "presence": presence, "split": split, "query_version": query_version, "query_version_digest": digest_json({"query_version": query_version, "query_id": query_id, "text": text, "family": family, "presence": presence, "split": split})}
        rows.append(_record("query", payload, "query"))
    eval_rows = [r for r in rows if r["payload"]["split"] == "EVALUATION"]
    dev_rows = [r for r in rows if r["payload"]["split"] == "DEVELOPMENT"]
    if len(eval_rows) != 32 or len(dev_rows) != 8 or sum(r["payload"]["presence"] == "POSITIVE" for r in eval_rows) != 24: raise ValueError("invalid query cardinality")
    return tuple(sorted(rows, key=lambda row: row["record_id"]))

def _rational(value):
    if isinstance(value, Mapping): return {"numerator": int(value["numerator"]), "denominator": int(value["denominator"])}
    return {"numerator": int(value[0]), "denominator": int(value[1])}

def _exact_rational(value, field: str) -> dict:
    """Reduce a declared uncertainty endpoint to an exact rational pair.

    Only integer components are accepted: ``float``/``bool`` inputs raise so no
    binary floating point can leak into interval or uncertainty evidence
    (CANONICAL_CONTRACTS.md §5).
    """
    if isinstance(value, Mapping):
        if set(value) != {"numerator", "denominator"}: raise ValueError("GOLD_UNCERTAINTY_INVALID")
        numerator, denominator = value["numerator"], value["denominator"]
    elif isinstance(value, (tuple, list)):
        if len(value) != 2: raise ValueError("GOLD_UNCERTAINTY_INVALID")
        numerator, denominator = value[0], value[1]
    else:
        raise ValueError("GOLD_UNCERTAINTY_INVALID")
    for component in (numerator, denominator):
        if isinstance(component, bool) or not isinstance(component, int): raise ValueError("GOLD_UNCERTAINTY_INVALID")
    if denominator == 0: raise ValueError("GOLD_UNCERTAINTY_INVALID")
    reduced = Fraction(numerator, denominator)
    return {"numerator": reduced.numerator, "denominator": reduced.denominator}

def _declared_uncertainty(event: Mapping) -> dict:
    declared = event.get("uncertainty")
    if declared is None: raise ValueError("GOLD_UNCERTAINTY_NOT_DECLARED")
    if not isinstance(declared, Mapping): raise ValueError("GOLD_UNCERTAINTY_INVALID")
    keys = set(declared)
    if keys == {"start", "end"}:
        start, end = declared["start"], declared["end"]
    elif keys == {"lower", "upper"}:
        start, end = declared["lower"], declared["upper"]
    else:
        raise ValueError("GOLD_UNCERTAINTY_INVALID")
    return {"start": _exact_rational(start, "start"), "end": _exact_rational(end, "end")}

def _declared_time_domain(event: Mapping) -> str:
    declared = event.get("time_domain")
    if declared is None: return DEFAULT_GOLD_TIME_DOMAIN
    if not isinstance(declared, str) or declared not in CANONICAL_TIME_DOMAINS:
        raise ValueError("GOLD_TIME_DOMAIN_NOT_CANONICAL")
    return declared

def _assertion_coordinate(value) -> tuple:
    """Reduce a declared coordinate to an exact rational identity pair.

    The gold schema's canonical rational is the ``{numerator, denominator}``
    mapping, while callers may also pass a 2-sequence.  Grouping assertions on
    ``tuple(value)`` conflates every mapping-form interval (the tuple of an
    object is its key names), which could bypass the frozen two-distinct-
    reviewers-per-assertion rule.  Both representations reduce to one exact
    pair; unparsable values keep a distinct raw identity and are still rejected
    by the typed per-event checks below.
    """
    try:
        rational = _exact_rational(value, "coordinate")
    except (TypeError, ValueError, KeyError):
        return ("UNPARSED", repr(value))
    return (rational["numerator"], rational["denominator"])


def build_gold_events(events: Iterable[Mapping], queries: Iterable[dict], label_version: str, *, reviewer_count: int = 2) -> tuple[dict, ...]:
    query_map = {r["payload"]["query_id"]: r["payload"] for r in queries}
    if reviewer_count != 2: raise ValueError("exactly two independent reviewers required")
    events = tuple(events)
    if not events:
        raise ValueError("gold event set cannot be empty")
    groups = {}
    for event in events:
        key = (
            event.get("query_id"),
            event.get("revision_id"),
            _assertion_coordinate(event.get("start")),
            _assertion_coordinate(event.get("end")),
        )
        groups.setdefault(key, []).append(event)
    for key, group in groups.items():
        reviewers = {str(event.get("reviewer_id")) for event in group if event.get("reviewer_id")}
        if len(group) != 2 or len(reviewers) != 2:
            raise ValueError("exactly two distinct reviewers required per assertion")
        grades = {event.get("grade") for event in group}
        if len(grades) > 1:
            refs = {event.get("adjudication_ref") for event in group}
            adjudicated = {event.get("adjudicated_grade") for event in group}
            if len(refs) != 1 or None in refs or len(adjudicated) != 1 or None in adjudicated:
                raise ValueError("reviewer disagreement requires consistent adjudication")
    rows = []
    for event in events:
        required = ("query_id", "revision_id", "reviewer_id", "grade", "rationale", "stream_index", "start", "end")
        if any(key not in event for key in required): raise ValueError("reviewer and typed gold fields required")
        query = query_map.get(event["query_id"])
        if query is None: raise ValueError("typed query/gold join failed")
        if query["split"] != "EVALUATION": raise ValueError("gold labels require evaluation query")
        if event["grade"] not in (0, 1, 2): raise ValueError("invalid grade")
        payload = {"assertion_id": opaque_id("assertion", event), "interval_id": opaque_id("interval", {"query_id": event["query_id"], "revision_id": event["revision_id"], "start": _assertion_coordinate(event["start"]), "end": _assertion_coordinate(event["end"])}), "query_id": event["query_id"], "revision_id": event["revision_id"], "reviewer_id": event["reviewer_id"], "grade": int(event["grade"]), "rationale": str(event["rationale"]), "label_version": label_version, "review_status": event.get("review_status", "UNREVIEWED"), "evidence_class": event.get("evidence_class", "VISUALLY_OBSERVED"), "stream_index": int(event["stream_index"]), "time_domain": _declared_time_domain(event), "origin": _rational(event.get("origin", (0, 1))), "start": _rational(event["start"]), "end": _rational(event["end"]), "uncertainty": _declared_uncertainty(event), "time_base": event.get("time_base", {"numerator": 1, "denominator": 1}), "endpoint_semantics": "HALF_OPEN", "precision": event.get("precision", "semantic-interval"), "producer_attempt_id": event.get("producer_attempt_id", opaque_id("attempt", label_version)), "refinement_eligibility": event.get("refinement_eligibility", "INELIGIBLE")}
        if event.get("adjudication_ref") is not None:
            payload["adjudication_ref"] = str(event["adjudication_ref"])
        rows.append(_record("gold_event", payload, "gold"))
    return tuple(sorted(rows, key=lambda row: row["record_id"]))

def ranking_inputs(queries: Iterable[dict]) -> dict:
    return {"queries": tuple({key: row["payload"][key] for key in ("query_id", "text", "query_version", "query_version_digest")} for row in queries)}
