"""Deterministic synthetic Gate-0 corpus generator.

This module produces a tiny, fully synthetic local input set that exercises the
executable Gate-0 experiment pipeline without any real media, model weights,
provider call or network access:

* ``synthetic-corpus.json`` — source occurrences, pinned probe JSON, selected
  stream evidence, deterministic decoder frames (integer PTS + rational time
  base) and per-frame fake embedding vectors;
* ``synthetic-labels.json`` — the frozen query set (24 positive / 8 absent /
  8 development), two-reviewer grade-2 gold events and the declared review
  grade plan;
* ``synthetic-query-vectors.json`` — fake text-embedding vectors for the
  semantic arm, kept separate from labels so the ranker can never read gold;
* ``media/*.bin`` — deterministic synthetic source bytes for hashing/probing.

The fixture is NOT Gate-0 evidence.  It exists to prove that the metadata arm,
the sampled semantic arm, deterministic ranking, evaluation metrics, repeat
replay and decision artifacts are wired under the frozen experiment contract.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

CORPUS_FILE = "synthetic-corpus.json"
LABELS_FILE = "synthetic-labels.json"
QUERY_VECTORS_FILE = "synthetic-query-vectors.json"
WINDOW_COUNT = 2
WINDOW_SECONDS = 4
TICKS = 8
DIMENSION = 8
REVIEWER_IDS = ("reviewer-1", "reviewer-2")
FAMILIES = ("APPEARANCE", "VISIBLE_ACTION", "INTERACTION", "SCENE_COMPOSITION_CAMERA_MOVEMENT")
EVALUATION_REVISIONS = ("rev_eval_sunrise", "rev_eval_office", "rev_eval_night")
DEVELOPMENT_REVISION = "rev_dev_probe"
LOCATOR_BY_REVISION = {
    "rev_eval_sunrise": "media/sunrise_beach_master.bin",
    "rev_eval_office": "media/office_interview_take.bin",
    "rev_eval_night": "media/night_traffic_city.bin",
    "rev_dev_probe": "media/dev_probe_calibration.bin",
}
SPLIT_BY_REVISION = {
    "rev_eval_sunrise": "EVALUATION",
    "rev_eval_office": "EVALUATION",
    "rev_eval_night": "EVALUATION",
    "rev_dev_probe": "DEVELOPMENT",
}
RELATIONS = (("rev_eval_sunrise", "rev_eval_office"),)
# Six of the twenty-four positive queries are declared semantic misses; the
# metadata floor is declared to establish only four.  These numbers are
# synthetic fixture declarations, not measured experiment results.
SEMANTIC_MISS_INDEXES = frozenset({3, 7, 11, 15, 19, 23})
METADATA_HIT_INDEXES = frozenset({0, 4, 8, 12})


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def normalized_vector(seed: str, *, dimension: int = DIMENSION) -> list[float]:
    raw = [((int.from_bytes(hashlib.sha256(f"{seed}:{i}".encode()).digest()[:4], "big") % 2001) - 1000) / 1000.0 for i in range(dimension)]
    norm = sum(value * value for value in raw) ** 0.5
    return [round(value / norm, 12) for value in raw]


def window_id(revision_id: str, window_index: int) -> str:
    return f"{revision_id}_window_{window_index}"


def window_interval(window_index: int) -> tuple[dict[str, int], dict[str, int]]:
    return ({"numerator": window_index * WINDOW_SECONDS, "denominator": 1},
            {"numerator": (window_index + 1) * WINDOW_SECONDS, "denominator": 1})


def _revision_frames(revision_id: str, *, time_base_num: int, time_base_den: int) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    ordinal = 0
    for window_index in range(WINDOW_COUNT):
        vector = normalized_vector(f"{revision_id}:window:{window_index}")
        for tick in range(TICKS):
            seconds_num = window_index * WINDOW_SECONDS * 2 + tick
            raw_pts = (seconds_num * time_base_den) // 2
            frames.append({
                "frame_id": f"{revision_id}_f{ordinal:03d}",
                "raw_pts_ticks": raw_pts,
                "time_base_num": time_base_num,
                "time_base_den": time_base_den,
                "decoder_ordinal": ordinal,
                "presentation_order": ordinal,
                "dts_ticks": raw_pts - (time_base_den // time_base_num),
                "frame_index": ordinal,
                "vector": vector,
            })
            ordinal += 1
    return frames


def build_corpus() -> dict[str, Any]:
    revisions = []
    for index, revision_id in enumerate(EVALUATION_REVISIONS + (DEVELOPMENT_REVISION,)):
        time_base_den = 90000 if revision_id in EVALUATION_REVISIONS else 30000
        revisions.append({
            "revision_id": revision_id,
            "occurrence_id": f"occ_{revision_id}",
            "content_id": f"content_{revision_id}",
            "locator": LOCATOR_BY_REVISION[revision_id],
            "relation_ids": [f"rel_{left}_{right}" for left, right in RELATIONS if revision_id in (left, right)],
            "split": SPLIT_BY_REVISION[revision_id],
            "window_count": WINDOW_COUNT,
            "origin_pts_ticks": 0,
            "probe": {
                "streams": [
                    {"index": 0, "codec_type": "video", "time_base": f"1/{time_base_den}", "width": 320, "height": 180},
                    {"index": 1, "codec_type": "audio", "time_base": "1/48000", "channels": 2},
                ],
                "format": {"duration": str(WINDOW_COUNT * WINDOW_SECONDS)},
            },
            "frames": _revision_frames(revision_id, time_base_num=1, time_base_den=time_base_den),
        })
    return {
        "schema_version": "gate0.synthetic-corpus.v1",
        "window_count": WINDOW_COUNT,
        "window_seconds": WINDOW_SECONDS,
        "evaluation_revisions": list(EVALUATION_REVISIONS),
        "development_revision": DEVELOPMENT_REVISION,
        "relations": [list(edge) for edge in RELATIONS],
        "revisions": revisions,
    }


_POSITIVE_TEXTS = (
    "sunrise beach red umbrella appears",
    "person wearing a blue jacket enters frame",
    "two people shake hands in the office",
    "camera pans across the night traffic",
    "a white van parks beside the kerb",
    "an interviewee points at the whiteboard",
    "sunrise light reflects on wet sand",
    "a cup is lifted from the desk",
    "the office door opens slowly",
    "night traffic headlights cross the junction",
    "a seagull lands on the beach railing",
    "the interviewer nods toward the camera",
    "pedestrians wait at the crossing",
    "a laptop screen changes colour",
    "a chair is dragged across the floor",
    "city lights flicker in the background",
    "shadow of a person on the office wall",
    "a taxi turns right at the corner",
    "sand is blown across the frame",
    "the whiteboard is wiped clean",
    "a hand reaches for the door handle",
    "rain starts falling on the street",
    "two colleagues review a printed chart",
    "the camera tilts up to the skyline",
)
_ABSENT_TEXTS = (
    "underwater dolphin pod",
    "snowboard halfpipe trick",
    "fireworks over a stadium",
    "close-up of a sleeping cat",
    "microscope slide with cells",
    "a wedding cake being cut",
    "rocket launch at dusk",
    "submarine periscope view",
)
_DEV_TEXTS = (
    "development sunrise test query",
    "development office test query",
    "development night test query",
    "development beach test query",
    "development traffic test query",
    "development interview test query",
    "development sand test query",
    "development city test query",
)


def query_id(index: int) -> str:
    return f"query_{index:02d}"


def _target_for_positive(index: int) -> tuple[str, int]:
    revision_id = EVALUATION_REVISIONS[index % len(EVALUATION_REVISIONS)]
    window_index = (index // len(EVALUATION_REVISIONS)) % WINDOW_COUNT
    return revision_id, window_index


def build_labels() -> dict[str, Any]:
    queries: list[dict[str, Any]] = []
    gold_events: list[dict[str, Any]] = []
    grade2_targets: list[dict[str, Any]] = []
    for index in range(24):
        query = {"query_id": query_id(index), "text": _POSITIVE_TEXTS[index], "family": FAMILIES[index % len(FAMILIES)], "presence": "POSITIVE", "split": "EVALUATION"}
        queries.append(query)
        revision_id, window_index = _target_for_positive(index)
        start, end = window_interval(window_index)
        for reviewer_id in REVIEWER_IDS:
            gold_events.append({
                "query_id": query["query_id"],
                "revision_id": revision_id,
                "reviewer_id": reviewer_id,
                "grade": 2,
                "rationale": "synthetic fixture grade-2 declaration",
                "stream_index": 0,
                "start": dict(start),
                "end": dict(end),
                "uncertainty": {"start": {"numerator": 0, "denominator": 1}, "end": {"numerator": 0, "denominator": 1}},
                "evidence_class": "EDITORIAL_INFERENCE",
            })
        if index not in SEMANTIC_MISS_INDEXES:
            grade2_targets.append({"query_id": query["query_id"], "blind_arm_token": "arm-b", "revision_id": revision_id, "window_index": window_index})
        if index in METADATA_HIT_INDEXES:
            grade2_targets.append({"query_id": query["query_id"], "blind_arm_token": "arm-a", "revision_id": revision_id, "window_index": window_index})
    for offset, text in enumerate(_ABSENT_TEXTS):
        queries.append({"query_id": query_id(24 + offset), "text": text, "family": FAMILIES[offset % len(FAMILIES)], "presence": "ABSENT", "split": "EVALUATION"})
    for offset, text in enumerate(_DEV_TEXTS):
        queries.append({"query_id": query_id(32 + offset), "text": text, "family": FAMILIES[offset % len(FAMILIES)], "presence": "POSITIVE" if offset % 2 == 0 else "ABSENT", "split": "DEVELOPMENT"})
    return {
        "schema_version": "gate0.synthetic-labels.v1",
        "query_version": "queries-synthetic-v1",
        "queries": queries,
        "gold_events": gold_events,
        "grade2_targets": grade2_targets,
        "semantic_miss_indexes": sorted(SEMANTIC_MISS_INDEXES),
        "metadata_hit_indexes": sorted(METADATA_HIT_INDEXES),
        "reviewers": list(REVIEWER_IDS),
    }


def build_query_vectors(labels: Mapping[str, Any]) -> dict[str, list[float]]:
    vectors: dict[str, list[float]] = {}
    for query in labels["queries"]:
        if query["split"] != "EVALUATION":
            continue
        if query["presence"] == "POSITIVE":
            index = int(query["query_id"].split("_")[1])
            revision_id, window_index = _target_for_positive(index)
            vectors[query["query_id"]] = normalized_vector(f"{revision_id}:window:{window_index}")
        else:
            vectors[query["query_id"]] = normalized_vector("absent:" + query["query_id"])
    return vectors


def media_bytes(revision_id: str) -> bytes:
    seed = hashlib.sha256(f"synthetic-media:{revision_id}".encode()).hexdigest()
    return (f"SYNTHETIC_MEDIA {revision_id} {seed}\n".encode("utf-8")) * 4


def write_fixtures(input_root: str | Path) -> dict[str, Path]:
    root = Path(input_root)
    (root / "media").mkdir(parents=True, exist_ok=True)
    corpus = build_corpus()
    labels = build_labels()
    query_vectors = build_query_vectors(labels)
    for revision in corpus["revisions"]:
        target = root / revision["locator"]
        target.write_bytes(media_bytes(revision["revision_id"]))
    paths = {
        "corpus": root / CORPUS_FILE,
        "labels": root / LABELS_FILE,
        "query_vectors": root / QUERY_VECTORS_FILE,
    }
    paths["corpus"].write_text(json.dumps(corpus, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["labels"].write_text(json.dumps(labels, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths["query_vectors"].write_text(json.dumps(query_vectors, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return paths


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluation_windows(corpus: Mapping[str, Any]) -> list[dict[str, Any]]:
    windows = []
    for revision_id in corpus["evaluation_revisions"]:
        for window_index in range(int(corpus["window_count"])):
            start, end = window_interval(window_index)
            windows.append({
                "revision_id": revision_id,
                "window_index": window_index,
                "window_id": window_id(revision_id, window_index),
                "start": start,
                "end": end,
            })
    return windows


def build_review_rows(labels: Mapping[str, Any], windows: Sequence[Mapping[str, Any]],
                      token_map: Sequence[Mapping[str, str]]) -> list[dict[str, Any]]:
    targets = {(row["query_id"], row["blind_arm_token"], row["revision_id"], int(row["window_index"])) for row in labels["grade2_targets"]}
    rows: list[dict[str, Any]] = []
    for query in labels["queries"]:
        if query["split"] != "EVALUATION":
            continue
        for token_row in token_map:
            token = str(token_row["blind_arm_token"])
            for window in windows:
                grade = 2 if (query["query_id"], token, window["revision_id"], int(window["window_index"])) in targets else 0
                for reviewer_id in REVIEWER_IDS:
                    rows.append({
                        "assertion_id": _assertion_id(query["query_id"], window["window_id"], token),
                        "query_id": query["query_id"],
                        "window_id": window["window_id"],
                        "blind_arm_token": token,
                        "reviewer_id": reviewer_id,
                        "grade": grade,
                        "ambiguity": "NONE",
                        "review_status": "ACCEPTED",
                        "assertion": {
                            "version": "gate0.assertion.synthetic.v1",
                            "text": query["text"],
                            "digest": _digest({"query_id": query["query_id"], "text": query["text"]}),
                        },
                    })
    rows.sort(key=lambda row: (row["query_id"], row["window_id"], row["blind_arm_token"], row["reviewer_id"]))
    return rows


def _assertion_id(query_id_value: str, window_id_value: str, token: str) -> str:
    material = hashlib.sha256(f"{query_id_value}|{window_id_value}|{token}".encode()).hexdigest()[:32]
    return f"assertion_{material}"


def _mapping_digest(token_map: Sequence[Mapping[str, str]], *, mapping_version: str, config_digest: str) -> str:
    ordered = sorted((dict(row) for row in token_map), key=lambda row: str(row["blind_arm_token"]).encode())
    return _digest({"mapping_version": mapping_version, "config_digest": config_digest, "token_map": ordered})


def write_review_input(path: str | Path, labels: Mapping[str, Any], windows: Sequence[Mapping[str, Any]],
                       token_map: Sequence[Mapping[str, str]], *, mapping_version: str = "gate0-v1",
                       config_digest: str = "0" * 64) -> Path:
    rows = build_review_rows(labels, windows, token_map)
    envelope = {
        "schema_version": "gate0.reviewer-input.v1",
        "input_digest": _digest({"schema_version": "gate0.reviewer-input.v1", "rows": rows}),
        "blind_mapping_digest": _mapping_digest(token_map, mapping_version=mapping_version, config_digest=config_digest),
        "rows": rows,
    }
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(envelope, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return target


def main(argv: Iterable[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root")
    args = parser.parse_args(list(argv) if argv is not None else None)
    paths = write_fixtures(args.input_root)
    for name, path in sorted(paths.items()):
        print(f"{name}={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
