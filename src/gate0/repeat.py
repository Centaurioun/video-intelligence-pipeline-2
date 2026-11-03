"""Retry identity and read-only repeatability comparison helpers."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from gate0.canonical_json import canonical_bytes
from gate0.failure import AttemptRecord
from gate0.identity import digest_bytes


def idempotency_key(run_id: str, stage: str, input_digest: str, config_digest: str, tool_environment_digest: str) -> str:
    # Length-prefixing makes the joined-byte scope unambiguous while remaining
    # independent of target rows (which are compared separately for retries).
    parts = (run_id, stage, input_digest, config_digest, tool_environment_digest)
    joined = b"".join(len(part.encode("utf-8")).to_bytes(8, "big") + part.encode("utf-8") for part in parts)
    return digest_bytes(joined)


def can_retry(previous: AttemptRecord, candidate: AttemptRecord) -> bool:
    return (previous.sealed and candidate.retry_of == previous.attempt_id and previous.retry_of is None and previous.error_class == "TRANSIENT_IO" and candidate.error_class == previous.error_class and previous.run_id == candidate.run_id and previous.stage == candidate.stage and previous.input_digest == candidate.input_digest and previous.config_digest == candidate.config_digest and previous.tool_environment_digest == candidate.tool_environment_digest and previous.target_set_digest == candidate.target_set_digest)


_RUNTIME_ONLY = frozenset({"runtime", "host", "rss", "timing", "timing_ms", "thermal", "temperature"})


def repeat_projection(value: Any) -> Any:
    """Return an identity-bearing projection, excluding host observations."""
    if isinstance(value, Mapping):
        return {str(key): repeat_projection(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0])) if str(key) not in _RUNTIME_ONLY}
    if isinstance(value, (list, tuple)):
        return [repeat_projection(item) for item in value]
    return value


def _first_difference(left: Any, right: Any, path: str = "$") -> str | None:
    if type(left) is not type(right):
        return path
    if isinstance(left, Mapping):
        for key in sorted(set(left) | set(right), key=str):
            if key not in left or key not in right:
                return f"{path}.{key}"
            found = _first_difference(left[key], right[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(left, list):
        for index, (a, b) in enumerate(zip(left, right)):
            found = _first_difference(a, b, f"{path}[{index}]")
            if found:
                return found
        return None if len(left) == len(right) else f"{path}[{min(len(left), len(right))}]"
    return None if left == right else path


@dataclass(frozen=True)
class RepeatComparison:
    equal: bool
    first_difference: str | None = None
    evidence_state: str = "MEASURED"


def compare_replays(expected: Any, observed: Any) -> RepeatComparison:
    left, right = repeat_projection(expected), repeat_projection(observed)
    difference = _first_difference(left, right)
    return RepeatComparison(difference is None, difference)


def frozen_input_digest(mode: str, manifest: Mapping[str, Any]) -> str:
    """Digest the exact ordered frozen-input object required by T10."""
    if mode not in {"frozen-index", "full-pipeline"}:
        raise ValueError("mode must be frozen-index or full-pipeline")
    supplied = manifest.get("frozen_input")
    if supplied is not None:
        if not isinstance(supplied, Mapping):
            raise ValueError("frozen input provenance mode mismatch")
        frozen = dict(supplied)
        stored_mode = frozen.pop("mode", None)
        if stored_mode is not None and stored_mode != mode:
            raise ValueError("frozen input provenance mode mismatch")
    else:
        frozen = {"source_revision_ids": manifest.get("source_revision_ids", []), "sample_manifest_digest": manifest.get("sample_manifest_digest", ""), "representation_digests": manifest.get("representation_digests", []), "ranking_digest": manifest.get("ranking_digest", ""), "metrics_digest": manifest.get("metrics_digest", ""), "config_digest": manifest.get("config_digest", "")}
        frozen["mode"] = mode
    required = {"mode", "source_revision_ids", "sample_manifest_digest", "representation_digests", "ranking_digest", "metrics_digest", "config_digest"}
    frozen["mode"] = mode
    if set(frozen) != required:
        raise ValueError("frozen input provenance fields mismatch")
    return digest_bytes(canonical_bytes(frozen))
