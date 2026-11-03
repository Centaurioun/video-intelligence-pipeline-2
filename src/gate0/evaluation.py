"""Local, blinded post-ranking evaluation for Gate-0.

This module deliberately accepts plain mappings at the stage boundary.  It does
not import the ranker or labels: callers provide the frozen ranking projection
and the post-ranking reviewer envelope, keeping the label firewall explicit.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from gate0.canonical_json import canonical_bytes


TOKENS = {"arm-a", "arm-b"}
FAMILIES = ("APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT")


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


@dataclass(frozen=True)
class ReviewerJudgmentInput:
    assertion_id: str
    query_id: str
    window_id: str
    blind_arm_token: str
    reviewer_id: str
    grade: int
    ambiguity: str
    review_status: str
    assertion: Mapping[str, Any]
    adjudication_ref: str | None = None


@dataclass(frozen=True)
class ReviewerInputEnvelope:
    schema_version: str
    input_digest: str
    blind_mapping_digest: str
    rows: tuple[ReviewerJudgmentInput, ...]


def _mapping_digest_for(token_map: Sequence[Mapping[str, str]], *, mapping_version: str = "gate0-v1", config_digest: str = "0" * 64) -> str:
    ordered = sorted((dict(row) for row in token_map), key=lambda row: str(row["blind_arm_token"]).encode())
    return _digest({"mapping_version": mapping_version, "config_digest": config_digest, "token_map": ordered})


def _input_digest_for(schema_version: str, rows: Sequence[Mapping[str, Any]]) -> str:
    return _digest({"schema_version": schema_version, "rows": list(rows)})


@dataclass(frozen=True)
class Metric:
    metric_id: str
    numerator: int
    denominator: int
    population_id: str
    benchmark_status: str
    validity: str
    query_version_digest: str
    gold_version_digest: str
    judgment_version_digest: str
    ranking_digest: str
    baseline_digest: str
    calculation_version: str
    arm_id: str | None = None
    family_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = {"metric_id": self.metric_id, "query_version_digest": self.query_version_digest,
                  "gold_version_digest": self.gold_version_digest, "judgment_version_digest": self.judgment_version_digest,
                  "ranking_digest": self.ranking_digest, "baseline_digest": self.baseline_digest,
                  "population_id": self.population_id, "numerator": self.numerator, "denominator": self.denominator,
                  "calculation_version": self.calculation_version, "benchmark_status": self.benchmark_status,
                  "validity": self.validity}
        return result


@dataclass(frozen=True)
class EvaluationResult:
    metrics: Mapping[str, Metric]
    judgments_digest: str
    decision_status: str
    per_query: Mapping[str, Mapping[str, int]]


def load_reviewer_input(path: str | Path, *, authorized_root: str | Path,
                        token_map: Sequence[Mapping[str, str]], expected_mapping_digest: str,
                        expected_input_digest: str | None = None,
                        expected_reviewer_ids: Iterable[str] | None = None,
                        expected_query_ids: Iterable[str] | None = None,
                        expected_window_ids: Iterable[str] | None = None,
                        mapping_version: str = "gate0-v1", config_digest: str = "0" * 64) -> ReviewerInputEnvelope:
    """Load and validate one blinded reviewer-input envelope.

    ``config_digest`` binds the envelope's blinding mapping to one configuration;
    the explicit executable path always supplies the run's canonical digest.
    ``expected_reviewer_ids``, when supplied, additionally requires the envelope's
    reviewer-identity set to equal the configured declared reviewer set (``None``
    preserves the legacy shape-only check for direct callers). ``expected_query_ids``
    and ``expected_window_ids``, when supplied, reject row references outside those
    run artifact identity sets without imposing coverage. The zero-digest defaults
    are compatibility-only and must never be used as run authority.
    """
    candidate = Path(path).resolve(); root = Path(authorized_root).resolve()
    if not candidate.is_file() or root not in candidate.parents:
        raise ValueError("review input must be a regular file beneath authorized root")
    try: raw = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc: raise ValueError("invalid reviewer input") from exc
    if not isinstance(raw, Mapping) or set(raw) != {"schema_version", "input_digest", "blind_mapping_digest", "rows"}:
        raise ValueError("reviewer input envelope has unknown or missing fields")
    if raw["schema_version"] != "gate0.reviewer-input.v1": raise ValueError("invalid reviewer input schema")
    computed_mapping = _mapping_digest_for(token_map, mapping_version=mapping_version, config_digest=config_digest)
    if raw["blind_mapping_digest"] != expected_mapping_digest or raw["blind_mapping_digest"] != computed_mapping: raise ValueError("wrong blinding mapping digest")
    if expected_input_digest is not None and raw["input_digest"] != expected_input_digest: raise ValueError("wrong reviewer input digest")
    if not isinstance(raw["rows"], list): raise ValueError("reviewer rows must be an array")
    allowed = {"assertion_id","query_id","window_id","blind_arm_token","reviewer_id","grade","ambiguity","review_status","adjudication_ref","assertion"}
    rows: list[ReviewerJudgmentInput] = []
    keys: set[tuple[str, str, str, str]] = set()
    known = {str(x["blind_arm_token"]): str(x["arm_id"]) for x in token_map}
    if set(known) != TOKENS or len(known) != 2: raise ValueError("exactly two blind arm tokens required")
    for item in raw["rows"]:
        if not isinstance(item, Mapping) or not set(item).issubset(allowed): raise ValueError("unknown reviewer field")
        required = {"assertion_id","query_id","window_id","blind_arm_token","reviewer_id","grade","ambiguity","review_status","assertion"}
        if set(item) - {"adjudication_ref"} != required: raise ValueError("incomplete reviewer row")
        token = item["blind_arm_token"]
        if token not in known: raise ValueError("unknown blind arm token")
        if item["grade"] not in (0, 1, 2) or item["ambiguity"] not in {"NONE","UNCERTAIN","AMBIGUOUS"}: raise ValueError("invalid reviewer grade")
        if item["review_status"] not in {"UNREVIEWED","ACCEPTED","REJECTED","AMBIGUOUS"}: raise ValueError("invalid review status")
        assertion = item["assertion"]
        if not isinstance(assertion, Mapping) or set(assertion) != {"version","text","digest"}: raise ValueError("invalid assertion projection")
        key = (str(item["query_id"]), str(item["window_id"]), str(token), str(item["reviewer_id"]))
        if key in keys: raise ValueError("duplicate reviewer judgment key")
        keys.add(key)
        rows.append(ReviewerJudgmentInput(*(str(item[k]) for k in ("assertion_id","query_id","window_id","blind_arm_token","reviewer_id")), int(item["grade"]), str(item["ambiguity"]), str(item["review_status"]), assertion, item.get("adjudication_ref")))
    if len({row.blind_arm_token for row in rows}) != 2: raise ValueError("exactly two blind arm tokens required")
    for parameter, values, attribute in (
        ("expected_query_ids", expected_query_ids, "query_id"),
        ("expected_window_ids", expected_window_ids, "window_id"),
    ):
        if values is None:
            continue
        if isinstance(values, (str, bytes, Mapping)):
            raise ValueError(f"{parameter} must be an iterable of identifiers")
        try:
            declared_values = tuple(values)
        except TypeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"{parameter} must be an iterable of identifiers") from exc
        if any(not isinstance(value, str) for value in declared_values):
            raise ValueError(f"{parameter} must contain only strings")
        allowed_values = frozenset(declared_values)
        if any(getattr(row, attribute) not in allowed_values for row in rows):
            raise ValueError(f"unknown reviewer {attribute}")
    if expected_reviewer_ids is not None:
        if isinstance(expected_reviewer_ids, (str, bytes, Mapping)):
            raise ValueError("expected_reviewer_ids must be an iterable of identifiers")
        try:
            declared_ids = tuple(expected_reviewer_ids)
        except TypeError as exc:  # pragma: no cover - defensive
            raise ValueError("expected_reviewer_ids must be an iterable of identifiers") from exc
        if any(not isinstance(reviewer_id, str) for reviewer_id in declared_ids):
            raise ValueError("expected_reviewer_ids must contain only strings")
        if {row.reviewer_id for row in rows} != frozenset(declared_ids):
            raise ValueError("reviewer identities do not match the declared reviewer set")
    computed_input = _input_digest_for(str(raw["schema_version"]), raw["rows"])
    if str(raw["input_digest"]) != computed_input: raise ValueError("wrong reviewer input digest")
    return ReviewerInputEnvelope(str(raw["schema_version"]), str(raw["input_digest"]), str(raw["blind_mapping_digest"]), tuple(rows))


def reviewer_judgments(envelope: ReviewerInputEnvelope, *, token_map: Sequence[Mapping[str, str]]) -> tuple[dict[str, Any], ...]:
    mapping = {str(row["blind_arm_token"]): str(row["arm_id"]) for row in token_map}
    if set(mapping) != TOKENS: raise ValueError("exactly two blind arm tokens required")
    groups: dict[tuple[str, str, str], list[ReviewerJudgmentInput]] = {}
    for row in envelope.rows: groups.setdefault((row.query_id, row.window_id, row.blind_arm_token), []).append(row)
    if any(len(group) != 2 or len({r.reviewer_id for r in group}) != 2 for group in groups.values()): raise ValueError("exactly two distinct reviewers required")
    result = []
    for key, group in groups.items():
        if any(r.review_status != "ACCEPTED" or r.ambiguity != "NONE" for r in group): raise ValueError("reviewer judgment is not final")
        if len({r.grade for r in group}) > 1:
            if any(not r.adjudication_ref for r in group) or len({r.adjudication_ref for r in group}) != 1: raise ValueError("reviewer disagreement requires adjudication")
            raise ValueError("adjudicated final grade must be identical")
        row = group[0]
        result.append({"query_id": row.query_id, "window_id": row.window_id, "arm_id": mapping[row.blind_arm_token], "grade": row.grade, "blind_arm_token": row.blind_arm_token})
    return tuple(sorted(result, key=lambda row: (row["query_id"], row["arm_id"], row["window_id"])))


def _metric(metric_id: str, num: int, den: int, pop: str, status: str, validity: str, args: Mapping[str, str], **kwargs: Any) -> Metric:
    return Metric(metric_id, num, den, pop, status, validity, args["query_version_digest"], args["gold_version_digest"], args["judgment_version_digest"], args["ranking_digest"], args["baseline_digest"], kwargs.pop("calculation_version"), kwargs.get("arm_id"), kwargs.get("family_id"))


def _exact(value: Any, *, field: str) -> Fraction:
    """Convert an interval coordinate to an exact rational value.

    The frozen contract carries interval evidence as rational wire objects
    (``{"numerator": int, "denominator": int}``, denominator positive) and
    requires exact half-open comparison.  Plain ints and finite floats remain
    accepted for backward compatibility; ``Fraction(float)`` is exact binary
    value conversion, never a rounded decimal approximation.
    """
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an exact rational number")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field} must be finite")
        return Fraction(value)
    if isinstance(value, Mapping):
        if set(value) != {"numerator", "denominator"}:
            raise ValueError(f"{field} must be an exact rational object")
        numerator, denominator = value["numerator"], value["denominator"]
        if isinstance(numerator, bool) or isinstance(denominator, bool):
            raise ValueError(f"{field} must be an exact rational number")
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise ValueError(f"{field} must be an exact rational number")
        if denominator <= 0:
            raise ValueError(f"{field} denominator must be positive")
        return Fraction(numerator, denominator)
    raise ValueError(f"{field} must be an exact rational number")


def _intersects(candidate: Mapping[str, Any], gold: Mapping[str, Any]) -> bool:
    # A window identity alone is not enough: the sample manifest's typed
    # mapping evidence is the authority for the technical-to-semantic join.
    if not candidate.get("mapping_ref") or not isinstance(candidate.get("mapping_ref"), str):
        raise ValueError("candidate mapping/origin/time-base evidence is required")
    for name in ("origin", "time_base"):
        value = candidate.get(name)
        if not isinstance(value, Mapping) or set(value) != {"numerator", "denominator"}:
            raise ValueError(f"candidate {name} evidence is invalid protocol")
        if not isinstance(value["numerator"], int) or not isinstance(value["denominator"], int) or value["denominator"] <= 0 or (name == "time_base" and value["numerator"] <= 0):
            raise ValueError(f"candidate {name} evidence is invalid protocol")
    if not gold.get("uncertainty") or not isinstance(gold.get("uncertainty"), Mapping):
        raise ValueError("gold uncertainty evidence is required")
    uncertainty = gold["uncertainty"]
    if set(uncertainty) != {"start", "end"}:
        raise ValueError("gold uncertainty evidence is invalid protocol")
    try:
        u_start = _exact(uncertainty["start"], field="gold uncertainty start")
        u_end = _exact(uncertainty["end"], field="gold uncertainty end")
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("gold uncertainty evidence is invalid protocol") from exc
    if u_start < 0 or u_end < 0:
        raise ValueError("gold uncertainty evidence is invalid protocol")
    try:
        c_start = _exact(candidate["start"], field="candidate interval start")
        c_end = _exact(candidate["end"], field="candidate interval end")
        g_start = _exact(gold["start"], field="gold interval start") - u_start
        g_end = _exact(gold["end"], field="gold interval end") + u_end
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("candidate/gold interval evidence is invalid protocol") from exc
    # Expand the gold interval by its explicit uncertainty, then match on a
    # non-empty half-open intersection with exact rational coordinates.
    return max(c_start, g_start) < min(c_end, g_end)


def evaluate(queries: Iterable[Mapping[str, Any]], judgments: Iterable[Mapping[str, Any]], *, ranking_digest: str, baseline_digest: str, gold_version_digest: str, query_version_digest: str, validity: str = "VALID", ranked_candidates: Iterable[Mapping[str, Any]] | None = None, gold_events: Iterable[Mapping[str, Any]] | None = None, coverage: Mapping[str, int] | None = None) -> EvaluationResult:
    query_rows = tuple(queries)
    eval_pos = tuple(row for row in query_rows if row.get("presence") == "POSITIVE" and row.get("split", "EVALUATION") == "EVALUATION")
    absent = tuple(row for row in query_rows if row.get("presence") == "ABSENT" and row.get("split", "EVALUATION") == "EVALUATION")
    if len(eval_pos) != 24: raise ValueError("expected exactly 24 positive evaluation queries")
    family_counts = {family: sum(row.get("family") == family for row in eval_pos) for family in FAMILIES}
    if family_counts != {family: 6 for family in FAMILIES}: raise ValueError("each positive family must contain exactly six queries")
    if coverage is not None and sum(int(coverage.get(k, 0)) for k in ("succeeded", "failed", "omitted", "quarantined")) != int(coverage.get("planned", -1)): raise ValueError("incomplete target coverage")
    js = tuple(judgments); jdigest = _digest(js); args = {"query_version_digest": query_version_digest, "gold_version_digest": gold_version_digest, "judgment_version_digest": jdigest, "ranking_digest": ranking_digest, "baseline_digest": baseline_digest}
    by_q = {(row["query_id"], row["arm_id"]): int(row["grade"] == 2) for row in js}
    if ranked_candidates is not None:
        candidates = tuple(ranked_candidates); gold = tuple(gold_events or ())
        by_q = {}
        for query in eval_pos + absent:
            for arm in ("metadata-floor", "offline-development-arm"):
                eligible = [c for c in candidates if c.get("query_id") == query["query_id"] and c.get("arm_id", c.get("representation_arm_id")) == arm and c.get("rank") is not None and int(c.get("rank")) <= 10]
                hits = []
                for candidate in eligible:
                    matching_gold = [g for g in gold if g.get("query_id") == query["query_id"] and g.get("grade") == 2 and g.get("revision_id", candidate.get("revision_id")) == candidate.get("revision_id") and _intersects(candidate, g)]
                    hits.append(any(any(j.get("query_id") == query["query_id"] and j.get("window_id") == candidate.get("window_id") and j.get("arm_id") == arm and j.get("grade") == 2 for j in js) for _ in matching_gold))
                by_q[(query["query_id"], arm)] = int(any(hits))
    semantic = tuple(by_q.get((row["query_id"], "offline-development-arm"), 0) for row in eval_pos); metadata = tuple(by_q.get((row["query_id"], "metadata-floor"), 0) for row in eval_pos)
    metrics: dict[str, Metric] = {}
    metrics["hit_at_10.metadata"] = _metric("hit_at_10.metadata", sum(metadata), 24, "evaluation_positive_24", "VALID" if validity == "VALID" else "INVALID_PROTOCOL", validity, args, calculation_version="hit_at_10.v1", arm_id="metadata-floor")
    metrics["hit_at_10.semantic"] = _metric("hit_at_10.semantic", sum(semantic), 24, "evaluation_positive_24", "VALID" if validity == "VALID" else "INVALID_PROTOCOL", validity, args, calculation_version="hit_at_10.v1", arm_id="offline-development-arm")
    metrics["paired_lift.semantic_minus_metadata"] = _metric("paired_lift.semantic_minus_metadata", sum(s - m for s, m in zip(semantic, metadata)), 24, "evaluation_positive_24", "VALID" if validity == "VALID" else "INVALID_PROTOCOL", validity, args, calculation_version="paired_lift.v1")
    for arm, metric_arm in (("metadata-floor", "metadata"), ("offline-development-arm", "semantic")):
        for family in FAMILIES:
            fam = tuple(row for row in eval_pos if row.get("family") == family)
            metrics[f"family_hit_at_10.{metric_arm}.{family.lower()}"] = _metric(f"family_hit_at_10.{metric_arm}.{family.lower()}", sum(by_q.get((r["query_id"], arm), 0) for r in fam), len(fam), f"evaluation_family_{family.lower()}_6", "VALID", validity, args, calculation_version="hit_at_10.v1", arm_id=arm, family_id=family)
        metrics[f"absent_query_diagnostic.{metric_arm}"] = _metric(f"absent_query_diagnostic.{metric_arm}", sum(by_q.get((r["query_id"], arm), 0) for r in absent), len(absent) or 1, "evaluation_absent_8", "VALID", validity, args, calculation_version="absent_query.v1", arm_id=arm)
    return EvaluationResult(metrics, jdigest, "VALID" if validity == "VALID" else validity, {r["query_id"]: {"semantic": s, "metadata": m} for r, s, m in zip(eval_pos, semantic, metadata)})
